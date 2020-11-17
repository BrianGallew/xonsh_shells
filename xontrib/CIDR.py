"""network address display/conversion

xontrib load CIDR

cidr 10.100.4.0/22
         CIDR range: 10.100.4.0/22
            Netmask: 255.255.252.0
    Network address: 10.100.4.0
  Broadcast address: 10.100.7.255
 First host address: 10.100.4.1
  Last host address: 10.100.7.254
Available addresses: 1022

Original code suggested by Adam Moskewicz, but rewritten to use the ipaddress module

"""

import ipaddress

__all__ = ()


def _cidr(args):
    "Simple wrapper around ipaddress.ip_network"
    arg = args[0]
    try:
        network = ipaddress.ip_network(arg, strict=False)
    except ValueError as the_exception:
        return the_exception
    hosts = list(network.hosts())
    return f"""         CIDR range: {network.with_prefixlen}
            Netmask: {network.netmask}
  Broadcast address: {network.broadcast_address}
 First host address: {hosts[0].compressed}
  Last host address: {hosts[-1].compressed}
Available addresses: {len(hosts)-2}
"""


# pylint: disable=undefined-variable
aliases["cidr"] = _cidr  # noqa: F821
