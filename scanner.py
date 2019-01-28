from logging import getLogger, ERROR

from scapy.all import *

getLogger("scapy.runtime").setLevel(ERROR)
conf.verb = 0

SYNACK = 0x12
RSTACK = 0x14


class SYNScanner:

    def __init__(self, ports, timeout):

        self.ports = ports
        self.timeout = timeout

    def scan(self, ip):

        srcPort = RandShort()
        SYNPacket = IP(dst=ip)/TCP(sport=srcPort, dport=self.ports, flags='S')
        RSTPacket = IP(dst=ip)/TCP(sport=srcPort, dport=self.ports, flags='R')

        SYNACKPackets, _ = sr(SYNPacket, timeout=self.timeout)
        send(RSTPacket)

        openPorts = [openPort for openPort in self.filterOpenPorts(SYNACKPackets, ip)]
        return openPorts

    def filterOpenPorts(self, packets, ip):
        filtBy = "%TCP.sport%"

        for packet in packets:
            _, response = packet
            isOpen = response and response.getlayer(TCP) and response.getlayer(TCP).flags == SYNACK
            if isOpen:
                openPort = TCP_SERVICES[response.sprintf(filtBy)]
                yield openPort