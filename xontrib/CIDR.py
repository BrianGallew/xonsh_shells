# -*- mode: python -*-
'''network address display/conversion

xontrib load CIDR

cidr 10.100.4.0/22
         CIDR range: 10.100.4.0/22
                    Netmask: 255.255.252.0
            Network address: 10.100.4.0
          Broadcast address: 10.100.7.255
         First host address: 10.100.4.1
          Last host address: 10.100.7.254
        Available addresses: 1022

Credit where credit is due:
This started from a conversation with Adam Moskewicz, but any coding mistakes are mine.
'''


class CIDR(object):
    '''Network address manipulation.'''
    thirtytwo = 0b11111111111111111111111111111111

    def __init__(self, network):
        if '/' in network:
            (subnet, self.bitlength) = network.split('/', 1)
        else:
            subnet = network
            self.bitlength = 32
        try:
            self.bitlength = int(self.bitlength)
            self.mask = 0
            for i in range(0, 32):
                self.mask <<= 1
                if i < self.bitlength:
                    self.mask += 1
        except ValueError:  # Hrm, maybe we got a netmask instead of a bitlength
            parts = self.bitlength.split('.')
            self.mask = (int(parts[0]) << 24) | (int(parts[1]) << 16) | (
                int(parts[2]) << 8) | int(parts[3])
            self.bitlength = str(bin(self.mask)).count('1')

        parts = subnet.split('.')
        self.ip = (int(parts[0]) << 24) | (int(parts[1]) << 16) | (
            int(parts[2]) << 8) | int(parts[3])

        self.first = self.convert((self.ip & self.mask) + 1)
        self.last = self.convert((self.ip | ~self.mask) - 1)
        self.subnet = self.convert(self.ip & self.mask)
        return

    def convert(self, number):
        'int to IP address'
        tmp = []
        tmp.append((number >> 24) & 0xff)
        tmp.append((number >> 16) & 0xff)
        tmp.append((number >> 8) & 0xff)
        tmp.append(number & 0xff)
        return '%d.%d.%d.%d' % tuple(tmp)

    def __repr__(self):
        s = """         CIDR range: %s/%d
                    Netmask: %s
            Network address: %s
          Broadcast address: %s
         First host address: %s
          Last host address: %s
        Available addresses: %d
        """
        return s % (self.subnet, self.bitlength, self.convert(self.mask),
                    self.convert(self.ip & self.mask),
                    self.convert(self.ip | ~self.mask), self.first, self.last,
                    (~self.mask & self.thirtytwo) - 1)


def _cidr(args):
    arg = args[0]
    if isinstance(arg, int) or arg.isnumeric():
        c = CIDR('0.0.0.0/0')
        return c.convert(int(arg))
    return CIDR(arg)
aliases['cidr'] = _cidr
