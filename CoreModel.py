import socket


class CoreModel:
    def __init__(self):
        self.defSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def scanIP(self, host, ports, timeout):
        if timeout == '':
            timeout = '3'
        self.defSocket.settimeout(3)
        openPorts = []
        for i in ports[0]:
            result = self.defSocket.connect_ex((host, int(i)))
            if result == 0:
                openPorts.append(i)
            self.defSocket.close()
        return openPorts
