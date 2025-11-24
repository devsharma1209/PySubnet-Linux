import ipaddress

class SubnetVisualizer:
    # ANSI Colors from teammate's code
    CYAN = "\033[36m"
    RED = "\033[31m"
    RESET = "\033[0m"

    def __init__(self, ip_cidr):
        if "/" not in ip_cidr:
            ip_cidr += "/24"  # Default assumption
        self.network = ipaddress.IPv4Network(ip_cidr, strict=False)
        self.ip_str = ip_cidr.split('/')[0]

    def get_binary_visuals(self):
        """Generates the binary representation strings."""
        # IP Binary
        octets = self.ip_str.split('.')
        binary_octets = [bin(int(octet))[2:].zfill(8) for octet in octets]
        bin_ip = '.'.join(binary_octets)

        # Netmask Binary
        bin_mask = str(bin(int(self.network.netmask))[2:].zfill(32))
        bin_mask = '.'.join([bin_mask[i:i+8] for i in range(0, len(bin_mask), 8)])

        return bin_ip, bin_mask

    def get_details(self):
        """Returns a dictionary of calculated network details."""
        hosts = list(self.network.hosts())
        
        if len(hosts) > 0:
            range_str = f"{hosts[0]} - {hosts[-1]}"
        else:
            range_str = "N/A (Point-to-Point)"

        return {
            "IP Address": self.ip_str,
            "Network Address": str(self.network.network_address),
            "CIDR": f"/{self.network.prefixlen}",
            "Netmask": str(self.network.netmask),
            "Broadcast": str(self.network.broadcast_address),
            "Usable Range": range_str,
            "Total Hosts": f"{self.network.num_addresses:,d}",
            "Usable Hosts": f"{len(hosts):,d}",
            "Is Private": str(self.network.is_private)
        }

    def get_subnets(self, new_prefix):
        """Splits the network into smaller subnets."""
        try:
            new_prefix = int(new_prefix)
            if new_prefix <= self.network.prefixlen:
                return [] 
            return list(self.network.subnets(new_prefix=new_prefix))
        except ValueError:
            return []