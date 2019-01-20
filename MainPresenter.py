import CoreModel
import Parser
import threading
import queue
from PyQt5.Qt import *
from netaddr import IPNetwork


class MainPresenter:
    def __init__(self, ui):
        self.coreModel = CoreModel.CoreModel()
        self.ui = ui
        self.threads = []
        self.isScanEnabled = False
        self.queue = queue.Queue()

    def startScan(self, ipRanges, portsStr, threadNumber, timeout):
        if timeout == '':
            timeout = '3'
        self.isScanEnabled = True
        cidrIPRanges = Parser.getCIDRFromRanges(ipRanges)
        ports = Parser.getPortsFromString(portsStr)
        ips = []
        for cidr in cidrIPRanges[0]:
            for ip in IPNetwork(cidr):
                ips.append(str(ip))
        for ip in ips:
            self.queue.put(ip)
        for i in range(int(threadNumber)):
            self.threads.append(ScanThread(self.queue, ports, timeout))
            self.setCurrentThreadsLabel(len(self.threads))
        for thread in self.threads:
            thread.signal.connect(self.setLogText)
            thread.finished.connect(self.onThreadExit)
            thread.start()

    def onThreadExit(self):
        if len(self.threads) == 0:
            self.setCurrentThreadsLabel(0)
            self.ui.startButton.setText("Start")
        else:
            self.setCurrentThreadsLabel(len(self.threads) - 1)

    def stopScan(self):
        self.isScanEnabled = False
        for thread in self.threads:
            thread.exit(0)
        self.threads = []
        self.queue = queue.Queue()

    def setLogText(self, string):
        self.ui.dataText.append(str(string) + '\n')

    def setCurrentThreadsLabel(self, threadNumber):
        self.ui.currentThreadsLabel.setText(str(threadNumber))


class ScanThread(QThread):

    signal = pyqtSignal(str)

    def __init__(self, scanQueue, ports, timeout, parent=None):
        QThread.__init__(self, parent)
        self.scanQueue = scanQueue
        self.coreModel = CoreModel.CoreModel()
        self.ports = ports
        self._stop_event = threading.Event()
        self.timeout = timeout

    def run(self):
        while True:
            if self.scanQueue.empty():
                self.exit(1)
            hostObject = self.scanQueue.get()
            open_ports = self.coreModel.scanIP(str(hostObject), self.ports, self.timeout)
            signalStr = ''.join(str(x) for x in open_ports)
            if(signalStr == ''):
                self.signal.emit(str(hostObject) + ' has no open ports!')
            else:
                self.signal.emit(str(hostObject) + ' has open ports: ' + signalStr)
            self.scanQueue.task_done()
