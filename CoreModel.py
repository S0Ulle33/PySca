import ipaddress

"""
class CoreModel:
    def __init__(self, timeout):
        self.defSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.defSocket.settimeout(int(timeout))

    def scanIP(self, host, ports):
        openPorts = []
        for port in ports:
            with self.defSocket as s:
                print(f"Connecting to {host}:{port}")
                result = s.connect_ex((host, int(port)))
                print(f"Result of {host}:{port} is {result}")
                if result == 0:
                    openPorts.append(port)
            self.defSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return openPorts
"""


class Target:

    def __init__(self, targets, ports):
        self.targets = targets
        self.ports = ports

    def isTarget(self, ip, port):
        if port not in self.ports:
            return False

        ip = ipaddress.ip_address(ip)
        for target in self.targets:
            try:
                if ip in target.hosts():
                    return True
            except AttributeError:
                if ip == target:
                    return True

        return False

    def range(self):
        for target in self.targets:
            try:
                for host in target.hosts():
                    yield host
            except AttributeError:
                yield target