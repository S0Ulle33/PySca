import CoreModel
import Parser
import socket
import queue
import datetime
from PyQt5.Qt import QThread, pyqtSignal
from RawTCP import TCPHeader, handle_packet, tcp_checksum


class MainPresenter:
    def __init__(self, ui):
        self.ui = ui
        self.coreModel = CoreModel

        self.listener_thread = ListenerThread(None)
        self.scan_threads = []
        self.scan_queue = queue.Queue()
        self.is_scan_enabled = False

    def start_scan(self, ip_ranges, ports, threads_number, timeout):
        ip_ranges = Parser.getCIDRFromRanges(ip_ranges)
        ports = Parser.getPortsFromString(ports)
        threads_number = int(threads_number)
        if not timeout:
            timeout = 3
        else:
            timeout = int(timeout)
        timeout = int(timeout)

        target = self.coreModel.Target(ip_ranges, ports)

        self.listener_thread.target = target
        self.listener_thread.signal.connect(self.log_text)
        self.listener_thread.start()

        for ip in target.range():
            self.scan_queue.put(str(ip))
        for t in range(threads_number):
            self.scan_threads.append(ScanThread(
                self.scan_queue, ports, timeout, self))
        for t in self.scan_threads:
            t.exit_signal.connect(self.on_thread_exit)
            t.start()

    def stop_scan(self):
        self.is_scan_enabled = False
        for t in self.threads:
            t.stop()
        self.listener_thread.stop()
        self.threads.clear()
        self.scan_queue.queue.clear()
        self.ui.set_running_threads_label("0")

    def log_text(self, text):
        self.ui.dataText.append(
            "[" + str(datetime.datetime.now()) + "] " + str(text))

    def on_thread_exit(self):
        if not all([t.is_running for t in self.threads]):
            self.is_scan_enabled = False
            self.ui.startButton.setText("Start")
        current_running_threads_label = self.get_running_threads_label()
        self.set_running_threads_label(current_running_threads_label - 1)

    def get_running_threads_label(self):
        return self.ui.currentThreadsLabel.getText()

    def set_running_threads_label(self, threadNumber):
        self.ui.currentThreadsLabel.setText(str(threadNumber))


class ListenerThread(QThread):

    signal = pyqtSignal(str)

    def __init__(self, target, parent=None):
        QThread.__init__(self, parent)
        self.target = target
        self.listen_socket = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.is_running = False

    def run(self):
        self.is_running = True
        while self.is_running:
            raw_packet = self.listen_socket.recvfrom(65565)
            ret = handle_packet(raw_packet)
            if ret:
                src_addr, src_port = ret
                if self.target.is_target(src_addr) and src_port in self.target.ports:
                    self.signal.emit(f"{src_addr} has open port: {src_port}")

    def stop(self):
        self.is_running = False
        self.wait()


class ScanThread(QThread):

    exit_signal = pyqtSignal(bool)

    def __init__(self, scan_queue, ports, timeout, presenter, parent=None):
        QThread.__init__(self, parent)
        self.scan_queue = scan_queue
        self.ports = ports
        # self.timeout = timeout
        # self._stop_event = threading.Event()
        # self.presenter = presenter
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                    socket.IPPROTO_TCP)
        self.source_ips = {}
        self.is_running = False

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

    def run(self):
        self.is_running = True
        while self.is_running:
            if self.scan_queue.empty():
                self.stop()
            for dst_port in self.ports:
                dest_ip = self.scan_queue.get()
                src_addr = self.get_source_ip(dest_ip)
                src_port = 54321
                make_tcpheader = TCPHeader(src_port, dst_port)
                tcp_header = make_tcpheader.get_struct()
                packet = make_tcpheader.get_struct(check=tcp_checksum(
                    src_addr, dest_ip, tcp_header), checksummed=True)
                try:
                    self.socket.sendto(packet, (dest_ip, 0))
                except Exception as e:
                    print(f"Error utilizing raw socket in send_raw_syn: {e}\n")

    def stop(self):
        self.is_running = False
        self.socket.close()
        self.exit_signal.emit()
        self.wait()
