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

    def is_target(self, ip):
        ip = ipaddress.ip_address(ip)
        for target in self.targets:
            if isinstance(target, ipaddress.IPv4Network):
                for host in target.hosts():
                    if ip == host:
                        return True
            else:
                if ip == target:
                    return True
        return False

    def range(self):
        for target in self.targets:
            # The target is just one ip, simply yield it:
            if isinstance(target, ipaddress.IPv4Address):
                yield target
            # The target is a network, yield every host in it:
            else:
                for host in target.hosts():
                    yield host
