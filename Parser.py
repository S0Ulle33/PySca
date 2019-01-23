import ipaddress


def getPortsFromString(ports):
    # Converts ports from form 20-40,100-900,40000-70000
    # It will automatically prune off non-existent ports (<1 >65535)
    if ports is None:
        return [21, 22, 23, 25, 80, 443, 110, 111, 135, 139, 445, 8080, 8443, 53, 143, 989, 990, 3306, 1080, 5554, 6667, 2222, 4444, 666, 6666, 1337, 2020, 31337] # Change to default ports from constant
    else:
        if "-" not in ports:
            tports = ports.split(",")
            print(tports)
        else:
            ports = ports.split(",")
            tports = []
            for port in ports:
                if "-" not in port:
                    tports.append(int(port))
                else:
                    # I made this one line because I wanted to
                    tports.extend(
                        list(range(int(port.split("-")[0]), int(port.split("-")[1]) + 1)))
    ports = [int(n) for n in tports if int(n) > 0 and int(n) < 65536]
    return ports


def getCIDRFromRanges(ips):
    ip_objects = set()
    inputs = [ip.strip() for ip in ips.split(',')]

    for input_ in inputs:
        try:
            if '-' in input_:
                input_ips = input_.split('-')
                ranges = {ipaddr for ipaddr in ipaddress.summarize_address_range(
                    ipaddress.IPv4Address(input_ips[0]),
                    ipaddress.IPv4Address(input_ips[1]))
                               }
                ip_objects.update(ranges)
            elif '/' in input_:
                network = ipaddress.ip_network(input_)
                ip_objects.add(network)
            else:
                ip = ipaddress.ip_address(input_)
                ip_objects.add(ip)
        except ValueError as e:
            print(e)

    for ip_obj in ip_objects:
        if not isinstance(ip_obj, ipaddress.IPv4Address):
            for ip in ip_obj.hosts():
                yield ip
        else:
            yield ip_obj
