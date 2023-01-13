import argparse
from ipaddress import AddressValueError, IPv4Address, IPv4Network, NetmaskValueError


class ValidNetworkOrIP(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        for address in values.split(','):
            try:
                IPv4Address(address)
            except AddressValueError:
                try:
                    IPv4Network(address)
                except (NetmaskValueError, ValueError):
                    raise argparse.ArgumentTypeError(f"valid_network_or_ip: {address} is not a valid network or ip address")

        setattr(namespace, self.dest, values)
