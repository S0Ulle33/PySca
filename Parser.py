import netaddr


def getCIDRFromRanges(str_ranges):
    str_ranges = str_ranges.replace(' ', '')
    ranges = []
    ips = []
    splitted_ranges = str_ranges.split(",")
    for i in splitted_ranges:
        ranges.append(i.split("-"))
    for i in ranges:
        if len(ranges[ranges.index(i)]) == 1:
            ips.append(netaddr.iprange_to_cidrs(i[0], i[0]))
        else:
            ips.append(netaddr.iprange_to_cidrs(i[0], i[1]))
    return ips


def getPortsFromString(str_ports):
    str_ports = str_ports.replace(" ", "")
    return [str_ports.split(",")]
