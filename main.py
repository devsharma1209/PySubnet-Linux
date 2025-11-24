import argparse
import sys
from core_calc import SubnetVisualizer
from linux_ops import LinuxOps

# Teammate's ANSI Colors
CYAN = "\033[36m"
RED = "\033[31m"
RESET = "\033[0m"

def print_banner():
    print(f"{CYAN}")
    print("╔════════════════════════════════════════╗")
    print("║      NET-VERIFY: Subnet & Linux Tool   ║")
    print("╚════════════════════════════════════════╝")
    print(f"{RESET}")

def print_kv(key, value):
    """Helper to print Key-Value pairs nicely"""
    print(f"{RESET}{key:<20}: {CYAN}{value}{RESET}")

def main():
    parser = argparse.ArgumentParser(description="Net-Verify Tool")
    parser.add_argument('--target', type=str, help="Target IP (e.g., 192.168.1.5/24)")
    parser.add_argument('--subnet', type=int, help="New CIDR to split into (e.g., 26)")
    parser.add_argument('--mode', choices=['calc', 'live'], default='calc', help="Simulated Calc or Live Linux Mode")
    
    args = parser.parse_args()

    # Enable colors on Windows
    if sys.platform == 'win32':
        import os
        os.system('')

    print_banner()

    # --- MODE SELECTION ---
    target_ip = args.target

    if args.mode == 'live':
        print(f"{RESET}[*] Mode: {CYAN}LIVE LINUX INTEGRATION{RESET}")
        print(f"{RESET}[*] Auto-detecting IP from OS...{RESET}")
        detected = LinuxOps.get_my_ip()
        if detected:
            print(f"{RESET}[+] Detected: {CYAN}{detected}{RESET}")
            target_ip = detected
        else:
            print(f"{RED}[!] Could not detect IP. Using fallback.{RESET}")
            target_ip = "192.168.1.1/24"
    
    if not target_ip:
        target_ip = input(f"{RESET}[?] Enter IP (192.168.0.1/24): {CYAN}") or "192.168.0.1/24"

    # --- CALCULATION PHASE ---
    try:
        viz = SubnetVisualizer(target_ip)
        details = viz.get_details()
        bin_ip, bin_mask = viz.get_binary_visuals()

        print("\n--- NETWORK DETAILS ---")
        print_kv("IP Address", details['IP Address'])
        print_kv("Binary IP", bin_ip) # Visual Requirement
        print_kv("Network Address", details['Network Address'])
        print_kv("Binary Netmask", bin_mask) # Visual Requirement
        print_kv("CIDR", details['CIDR'])
        print_kv("Usable Range", details['Usable Range'])
        print_kv("Hosts", details['Usable Hosts'])
        print_kv("Private Network", details['Is Private'])

        # --- SUBNETTING PHASE ---
        if args.subnet:
            print(f"\n--- SUBNETTING into /{args.subnet} ---")
            subnets = viz.get_subnets(args.subnet)
            if not subnets:
                print(f"{RED}Invalid subnet prefix.{RESET}")
            else:
                print(f"{'Network':<18} | {'Broadcast':<18} | {'Range Start'}")
                print("-" * 55)
                for sn in subnets[:10]: # Limit to 10 for display safety
                    hosts = list(sn.hosts())
                    start = str(hosts[0]) if hosts else "N/A"
                    print(f"{CYAN}{str(sn.network_address):<18} {RESET}| {str(sn.broadcast_address):<18} | {start}")
                if len(subnets) > 10:
                    print(f"... and {len(subnets)-10} more.")

        # --- VERIFICATION PHASE (Linux Only) ---
        if args.mode == 'live':
            print("\n--- LIVE REACHABILITY CHECK (Linux Ping) ---")
            
            # Let's ping the Gateway (usually .1) and the Broadcast-1
            net_base = ".".join(details['Network Address'].split('.')[:3])
            
            # Define targets to scan
            targets = [
                details['Network Address'], # The Network ID
                f"{net_base}.1",            # Likely Gateway
                f"{net_base}.254",          # Likely High Host
                details['IP Address']       # Self
            ]
            
            print(f"{'Target IP':<20} | {'Status'}")
            print("-" * 35)
            
            for t in targets:
                is_up = LinuxOps.ping_host(t)
                status = f"{CYAN}UP (Reachable){RESET}" if is_up else f"{RED}DOWN{RESET}"
                print(f"{t:<20} | {status}")

    except Exception as e:
        print(f"\n{RED}[!] Error: {e}{RESET}")

if __name__ == "__main__":
    main()