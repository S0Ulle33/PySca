import socket


class CoreModel:
    def __init__(self, timeout):
        self.defSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.defSocket.settimeout(int(timeout))

    def scanIP(self, host, ports):
        openPorts = []
        for i in ports[0]:
            result = self.defSocket.connect_ex((host, int(i)))
            if result == 0:
                openPorts.append(i)
            self.defSocket.close()
        return openPorts
