from ipaddress import AddressValueError, IPv4Address, IPv4Network


class IPFilter:

    def __init__(self, addresses) -> None:
        self.ips = []
        self.networks = []

        for address in addresses:
            try:
                ip = IPv4Address(address)
                self.ips.append(ip)
            except AddressValueError:
                net = IPv4Network(address)
                self.networks.append(net)

    def is_allow(self, address: str) -> bool:
        ip = IPv4Address(address)

        if ip in self.ips:
            return True

        for network in self.networks:
            if ip in network:
                return True

        return False