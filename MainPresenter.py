import datetime
import queue
import socket
from time import sleep

from PyQt5.Qt import QThread, pyqtSignal
from PyQt5.QtCore import QObject, pyqtSlot

import CoreModel
import Parser
from RawTCP import TCPHeader, handle_packet, tcp_checksum


class MainPresenter:

    def __init__(self, ui):
        self.ui = ui
        self.coreModel = CoreModel

        self.is_scan_enabled = False
        self.scan_queue = queue.Queue()
        self.__listener_thread = None
        self.__scan_threads = []

    def start_scan(self, ip_ranges, ports, threads_number, timeout):
        ip_ranges = Parser.getCIDRFromRanges(ip_ranges)
        ports = Parser.getPortsFromString(ports)
        threads_number = int(threads_number)
        if not timeout:
            timeout = 3
        else:
            timeout = int(timeout)

        target = self.coreModel.Target(ip_ranges, ports)

        listener_worker = ListenerWorker(target)
        listener_thread = QThread()
        listener_worker.open_port_signal.connect(self.log_text)
        listener_worker.moveToThread(listener_thread)
        listener_worker.finished_signal.connect(listener_thread.exit)
        listener_worker.finished_signal.connect(self.worker_exit)
        listener_thread.started.connect(listener_worker.work)
        self.__listener_thread = (listener_worker, listener_thread)
        listener_thread.start()

        for ip in target.range():
            self.scan_queue.put(str(ip))
        for _ in range(threads_number):
            scan_worker = ScanWorker(self.scan_queue, ports, self)
            scan_thread = QThread()
            scan_worker.log.connect(self.log_text)
            scan_worker.moveToThread(scan_thread)
            scan_worker.finished.connect(scan_thread.exit)
            scan_worker.finished.connect(self.worker_exit)
            scan_thread.started.connect(scan_worker.work)
            self.__scan_threads.append((scan_worker, scan_thread))
        self.set_running_threads_label(len(self.__scan_threads) + 1)
        [t[1].start() for t in self.__scan_threads]
        

    def worker_exit(self):
        self.set_running_threads_label(int(self.ui.currentThreadsLabel.text()) - 1)
        if all(not worker.is_running for worker, _ in self.__scan_threads) and not self.__listener_thread[0].is_running:
            self.is_scan_enabled = False
            self.__scan_threads.clear()
            with self.scan_queue.mutex:
                self.scan_queue.queue.clear()
                self.scan_queue.all_tasks_done.notify_all()
                self.scan_queue.unfinished_tasks = 0
            self.ui.startButton.setText("Start")
    
    def stop_scan(self):
        self.stop_workers()
        self.is_scan_enabled = False
        self.__scan_threads.clear()
        with self.scan_queue.mutex:
            self.scan_queue.queue.clear()
            self.scan_queue.all_tasks_done.notify_all()
            self.scan_queue.unfinished_tasks = 0
        self.ui.startButton.setText("Start")
        self.set_running_threads_label("0")

    def stop_workers(self):
        try:
            for worker, _  in self.__scan_threads:
                if worker.is_running:
                    worker.stop()
            if self.__listener_thread[0].is_running:
                self.__listener_thread[0].stop()
        except Exception as e:
            self.log_text(e)

    def log_text(self, text):
        print(text)
        self.ui.dataText.append(
            "[" + str(datetime.datetime.now()) + "] " + str(text))

    def set_running_threads_label(self, threadNumber):
        self.ui.currentThreadsLabel.setText(str(threadNumber))


class ListenerWorker(QObject):

    MAX_RETRIES = 5
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)

    def __init__(self, target, **kwds):
        super().__init__(**kwds)
        self.target = target
        self.ip_ports = {str(ip):self.target.ports[:] for ip in list(self.target.range())}
        self.listen_socket = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.is_running = True

    @pyqtSlot()
    def work(self):
        self.log_signal.emit("ListenerWorker::work()")
        RETRIES = 0
        while self.is_running:
            if not all([item[1] for item in self.ip_ports.items()]) or RETRIES >= MAX_RETRIES:
                self.stop()
            raw_packet = self.listen_socket.recvfrom(65565)
            is_open, ret = handle_packet(raw_packet)
            src_addr, src_port = ret
            if self.target.is_target(src_addr, src_port):
                if is_open:
                    self.log_signal.emit(f"{src_addr} has open port: {src_port}")
                self.ip_ports[src_addr].remove(src_port)
                RETRIES = 0
            else:
                RETRIES += 1

    def stop(self):
        self.log_signal.emit("ListenerWorker::stop()")
        self.is_running = False
        self.finished_signal.emit()


class ScanWorker(QObject):

    finished = pyqtSignal()
    log = pyqtSignal(str)

    def __init__(self, scan_queue, ports, presenter, **kwds):
        super().__init__(**kwds)

        self.scan_queue = scan_queue
        self.ports = ports
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.presenter = presenter
        self.source_ips = {}
        self.is_running = True

    def get_source_ip(self, dst_addr):
        try:
            if dst_addr in self.source_ips:
                return self.source_ips[dst_addr]
            else:
                self.source_ips[dst_addr] = [(s.connect((dst_addr, 53)), s.getsockname()[0], s.close(
                )) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
                return self.source_ips[dst_addr]
        except Exception:
            print("Something went wrong in get_source_ip, results might be wrong\n")

    @pyqtSlot()
    def work(self):
        self.log.emit("ScanWorker::work()")
        while self.is_running:
            if self.scan_queue.empty():
                self.stop()
            dest_ip = self.scan_queue.get()
            for dst_port in self.ports:
                src_addr = self.get_source_ip(dest_ip)
                src_port = 54321
                make_tcpheader = TCPHeader(src_port, dst_port)
                tcp_header = make_tcpheader.get_struct()
                packet = make_tcpheader.get_struct(check=tcp_checksum(src_addr, dest_ip, tcp_header), checksummed=True)
                try:
                    self.socket.sendto(packet, (dest_ip, 0))
                except Exception as e:
                    print(f"Error utilizing raw socket in send_raw_syn: {e}\n")
            self.scan_queue.task_done()

    def stop(self):
        self.log.emit("ScanWorker::stop()")
        self.is_running = False
        self.finished.emit()
