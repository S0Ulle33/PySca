import datetime
import queue
import socket
from time import sleep

from PyQt5.Qt import QThread, pyqtSignal
from PyQt5.QtCore import QObject, pyqtSlot

import CoreModel
import parser
from scanner import SYNScanner


class MainPresenter:

    def __init__(self, ui):
        self.ui = ui
        self.coreModel = CoreModel

        self.isScanEnabled = False
        self.scanQueue = queue.Queue()
        self.__listenerThread = None
        self.__scanThreads = []

    def startScan(self, IPRanges, ports, threadsNumber, timeout):
        IPRanges = parser.getCIDRFromRanges(IPRanges)
        ports = parser.getPortsFromString(ports)
        threadsNumber = int(threadsNumber)
        if not timeout:
            timeout = 3
        else:
            timeout = int(timeout)
        scaner = SYNScanner(ports, timeout)
        target = self.coreModel.Target(IPRanges, ports)

        for ip in target.range():
            self.scanQueue.put(str(ip))
        for _ in range(threadsNumber):
            scanWorker = ScanWorker(scaner, self.scanQueue)
            scanThread = QThread()
            scanWorker.logSignal.connect(self.logText)
            scanWorker.moveToThread(scanThread)
            scanWorker.finishedSignal.connect(scanThread.exit)
            scanWorker.finishedSignal.connect(self.workerExit)
            scanThread.started.connect(scanWorker.work)
            self.__scanThreads.append((scanWorker, scanThread))

        self.setRunningThreadsLabel(len(self.__scanThreads))
        [t[1].start() for t in self.__scanThreads]

    def workerExit(self):
        self.setRunningThreadsLabel(int(self.ui.currentThreadsLabel.text()) - 1)
        if all(not worker.isRunning for worker, _ in self.__scanThreads):
            self.isScanEnabled = False
            self.__scanThreads.clear()
            with self.scanQueue.mutex:
                self.scanQueue.queue.clear()
                self.scanQueue.all_tasks_done.notify_all()
                self.scanQueue.unfinishedSignal_tasks = 0
            self.ui.startButton.setText("Start")

    def stopScan(self):
        try:
            for worker, _ in self.__scanThreads:
                if worker.isRunning:
                    worker.stop()
        except Exception as e:
            self.logText(e)

    def logText(self, text):
        print(text)
        self.ui.dataText.append(
            "[" + str(datetime.datetime.now()) + "] " + str(text))

    def setRunningThreadsLabel(self, threadNumber):
        self.ui.currentThreadsLabel.setText(str(threadNumber))

"""
class ListenerWorker(QObject):

    finishedSignal = pyqtSignal()
    logSignal = pyqtSignal(str)

    def __init__(self, target, scanThreads,**kwds):
        super().__init__(**kwds)
        self.target = target
        self.IPPortDict = {str(ip):self.target.ports[:] for ip in list(self.target.range())}
        self.listenSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.isRunning = True

        self.__scanThreads = scanThreads

    @pyqtSlot()
    def work(self):
        self.logSignal.emit("ListenerWorker::work()")
        MAX_RETRIES = 5
        RETRIES = 0
        while self.isRunning:
            if not (all([item[1] for item in self.IPPortDict.items()])
                or RETRIES >= MAX_RETRIES) and all(not t.isRunning for _, t in self.__scanThreads):
                self.stop()
                break
            rawPacket = self.listenSocket.recvfrom(65565)
            isOpen, ret = handle_packet(rawPacket)
            srcAddress, srcPort = ret
            if self.target.isTarget(srcAddress, srcPort):
                if isOpen:
                    self.logSignal.emit(f"{srcAddress} has open port: {srcPort}")
                try:
                    self.IPPortDict[srcAddress].remove(srcPort)
                except ValueError as e:
                    self.logSignal.emit(f"Error in self.IPPortDict[srcAddress].remove(srcPort): {e} (no {srcPort} in IPPortDict[{srcAddress}])")
                    pass
                RETRIES = 0
            else:
                RETRIES += 1

    def stop(self):
        self.logSignal.emit("ListenerWorker::stop()")
        self.isRunning = False
        self.listenSocket.close()
        self.finishedSignal.emit()
"""

class ScanWorker(QObject):

    finishedSignal = pyqtSignal()
    logSignal = pyqtSignal(str)

    def __init__(self, scaner, scanQueue, **kwds):
        super().__init__(**kwds)

        self.scaner = scaner
        self.scanQueue = scanQueue
        self.isRunning = True

    @pyqtSlot()
    def work(self):
        #self.logSignal.emit("ScanWorker::work()")
        while self.isRunning:
            if self.scanQueue.empty():
                self.stop()
            dstIP = self.scanQueue.get()
            openPorts = self.scaner.scan(dstIP)
            for openPort in openPorts:
                self.logSignal.emit(f"{dstIP} has open port: {openPort}")
            self.scanQueue.task_done()

    def stop(self):
        #self.logSignal.emit("ScanWorker::stop()")
        self.isRunning = False
        self.finishedSignal.emit()
