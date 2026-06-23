"""Interactive CLI interface for TUNNELpeak"""

import sys
from pathlib import Path
from typing import Optional

from src.tunnel_manager import TunnelManager
from src.tunnel_config import TunnelConfig, TunnelType, EncryptionMethod
from src.utils.logger import (
    print_banner, print_header, print_separator,
    print_success, print_error, print_warning, print_info, Colors
)
from src.utils.system import check_root, validate_ip, validate_ipv4, validate_ipv6


class TunnelPeakCLI:
    """Interactive CLI interface"""
    
    def __init__(self):
        check_root()
        self.manager = TunnelManager()
        self.running = True
    
    def run(self):
        """Main CLI loop"""
        print_banner()
        
        while self.running:
            print_separator()
            print(f"{Colors.BOLD}{Colors.CYAN}TUNNELpeak Main Menu{Colors.RESET}")
            print_separator()
            print("1. Create Tunnel")
            print("2. List Tunnels")
            print("3. Start Tunnel")
            print("4. Stop Tunnel")
            print("5. Delete Tunnel")
            print("6. Test Tunnel")
            print("7. Tunnel Status")
            print("8. Export Configuration")
            print("9. Import Configuration")
            print("10. System Diagnostics")
            print("11. Exit")
            print_separator()
            
            choice = input(f"{Colors.YELLOW}Enter your choice (1-11): {Colors.RESET}").strip()
            
            if choice == "1":
                self.menu_create_tunnel()
            elif choice == "2":
                self.menu_list_tunnels()
            elif choice == "3":
                self.menu_start_tunnel()
            elif choice == "4":
                self.menu_stop_tunnel()
            elif choice == "5":
                self.menu_delete_tunnel()
            elif choice == "6":
                self.menu_test_tunnel()
            elif choice == "7":
                self.menu_tunnel_status()
            elif choice == "8":
                self.menu_export_config()
            elif choice == "9":
                self.menu_import_config()
            elif choice == "10":
                self.menu_system_diagnostics()
            elif choice == "11":
                self.running = False
                print_success("Goodbye!")
            else:
                print_error("Invalid choice!")
    
    def menu_create_tunnel(self):
        """Create tunnel menu"""
        print_header("Create New Tunnel")
        
        # Tunnel type selection
        print(f"{Colors.CYAN}Available Tunnel Types:{Colors.RESET}")
        for i, ttype in enumerate(TunnelType, 1):
            print(f"{i}. {ttype.value.upper()}")
        
        while True:
            try:
                type_choice = int(input(f"{Colors.YELLOW}Select tunnel type (1-{len(TunnelType)}): {Colors.RESET}"))
                if 1 <= type_choice <= len(TunnelType):
                    tunnel_type = list(TunnelType)[type_choice - 1]
                    break
                else:
                    print_error("Invalid choice!")
            except ValueError:
                print_error("Please enter a number!")
        
        config = TunnelConfig()
        config.tunnel_type = tunnel_type
        
        # Get basic configuration
        config.interface_name = input(f"{Colors.YELLOW}Interface name (default: tunnel0): {Colors.RESET}").strip() or "tunnel0"
        config.description = input(f"{Colors.YELLOW}Description (optional): {Colors.RESET}").strip()
        
        # Get network IPs
        while True:
            config.local_ip = input(f"{Colors.YELLOW}Local IP address: {Colors.RESET}").strip()
            if validate_ip(config.local_ip):
                break
            print_error("Invalid IP address!")
        
        while True:
            config.remote_ip = input(f"{Colors.YELLOW}Remote IP address: {Colors.RESET}").strip()
            if validate_ip(config.remote_ip):
                break
            print_error("Invalid IP address!")
        
        config.private_ip = input(f"{Colors.YELLOW}Private IP address (optional): {Colors.RESET}").strip() or ""
        if config.private_ip and not validate_ip(config.private_ip):
            print_warning("Invalid private IP, skipping")
            config.private_ip = ""
        
        config.private_ipv6 = input(f"{Colors.YELLOW}Private IPv6 address (optional): {Colors.RESET}").strip() or None
        if config.private_ipv6 and not validate_ipv6(config.private_ipv6):
            print_warning("Invalid IPv6 address, skipping")
            config.private_ipv6 = None
        
        # MTU
        mtu_input = input(f"{Colors.YELLOW}MTU size (default: 1500): {Colors.RESET}").strip()
        if mtu_input:
            try:
                config.mtu = int(mtu_input)
            except ValueError:
                print_warning("Invalid MTU, using default 1500")
                config.mtu = 1500
        
        # Tunnel ID (for GRE, VXLAN, etc.)
        if config.tunnel_type in [TunnelType.GRE, TunnelType.VXLAN, TunnelType.GENEVE]:
            tunnel_id_input = input(f"{Colors.YELLOW}Tunnel ID (default: 1): {Colors.RESET}").strip()
            if tunnel_id_input:
                try:
                    config.tunnel_id = int(tunnel_id_input)
                except ValueError:
                    print_warning("Invalid tunnel ID, using default 1")
        
        # Encryption options
        if input(f"{Colors.YELLOW}Enable encryption? (y/n, default: n): {Colors.RESET}").lower() == 'y':
            config.enable_encryption = True
            config.preshared_key = input(f"{Colors.YELLOW}Pre-Shared Key: {Colors.RESET}").strip()
            
            if config.tunnel_type == TunnelType.IPSEC:
                print(f"{Colors.CYAN}Encryption Methods:{Colors.RESET}")
                for i, method in enumerate(EncryptionMethod, 1):
                    print(f"{i}. {method.value}")
                
                try:
                    method_choice = int(input(f"{Colors.YELLOW}Select encryption method: {Colors.RESET}"))
                    if 1 <= method_choice <= len(EncryptionMethod):
                        config.encryption_method = list(EncryptionMethod)[method_choice - 1]
                except ValueError:
                    pass
        
        # WireGuard specific options
        if config.tunnel_type == TunnelType.WIREGUARD:
            wg_port = input(f"{Colors.YELLOW}WireGuard port (default: 51820): {Colors.RESET}").strip()
            if wg_port:
                try:
                    config.wireguard_port = int(wg_port)
                except ValueError:
                    pass
            
            config.wireguard_peerkey = input(f"{Colors.YELLOW}Peer public key (optional): {Colors.RESET}").strip() or None
        
        # Save tunnel
        tunnel_name = config.interface_name
        if self.manager.create_tunnel(config, tunnel_name):
            print_success(f"Tunnel '{tunnel_name}' created successfully!")
        else:
            print_error(f"Failed to create tunnel '{tunnel_name}'")
    
    def menu_list_tunnels(self):
        """List all tunnels"""
        print_header("Active Tunnels")
        
        tunnels = self.manager.list_tunnels()
        
        if not tunnels:
            print_warning("No tunnels found")
            return
        
        for tunnel in tunnels:
            print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
            print(f"{Colors.BOLD}Name:{Colors.RESET} {tunnel['name']}")
            print(f"{Colors.BOLD}Type:{Colors.RESET} {tunnel['type'].upper()}")
            print(f"{Colors.BOLD}Interface:{Colors.RESET} {tunnel['interface']}")
            print(f"{Colors.BOLD}Status:{Colors.RESET} {tunnel['status']}")
            print(f"{Colors.BOLD}Local IP:{Colors.RESET} {tunnel['local_ip']}")
            print(f"{Colors.BOLD}Remote IP:{Colors.RESET} {tunnel['remote_ip']}")
            if tunnel['private_ip']:
                print(f"{Colors.BOLD}Private IP:{Colors.RESET} {tunnel['private_ip']}")
            print(f"{Colors.BOLD}MTU:{Colors.RESET} {tunnel['mtu']}")
    
    def menu_start_tunnel(self):
        """Start tunnel menu"""
        print_header("Start Tunnel")
        
        tunnels = self.manager.list_tunnels()
        if not tunnels:
            print_warning("No tunnels found")
            return
        
        for i, tunnel in enumerate(tunnels, 1):
            print(f"{i}. {tunnel['name']} ({tunnel['type'].upper()}) - {tunnel['status']}")
        
        try:
            choice = int(input(f"{Colors.YELLOW}Select tunnel (1-{len(tunnels)}): {Colors.RESET}"))
            if 1 <= choice <= len(tunnels):
                tunnel_name = tunnels[choice - 1]['name']
                self.manager.start_tunnel(tunnel_name)
        except ValueError:
            print_error("Invalid choice!")
    
    def menu_stop_tunnel(self):
        """Stop tunnel menu"""
        print_header("Stop Tunnel")
        
        tunnels = self.manager.list_tunnels()
        if not tunnels:
            print_warning("No tunnels found")
            return
        
        for i, tunnel in enumerate(tunnels, 1):
            print(f"{i}. {tunnel['name']} ({tunnel['type'].upper()}) - {tunnel['status']}")
        
        try:
            choice = int(input(f"{Colors.YELLOW}Select tunnel (1-{len(tunnels)}): {Colors.RESET}"))
            if 1 <= choice <= len(tunnels):
                tunnel_name = tunnels[choice - 1]['name']
                self.manager.stop_tunnel(tunnel_name)
        except ValueError:
            print_error("Invalid choice!")
    
    def menu_delete_tunnel(self):
        """Delete tunnel menu"""
        print_header("Delete Tunnel")
        
        tunnels = self.manager.list_tunnels()
        if not tunnels:
            print_warning("No tunnels found")
            return
        
        for i, tunnel in enumerate(tunnels, 1):
            print(f"{i}. {tunnel['name']} ({tunnel['type'].upper()})")
        
        try:
            choice = int(input(f"{Colors.YELLOW}Select tunnel (1-{len(tunnels)}): {Colors.RESET}"))
            if 1 <= choice <= len(tunnels):
                tunnel_name = tunnels[choice - 1]['name']
                if input(f"{Colors.RED}Are you sure? (y/n): {Colors.RESET}").lower() == 'y':
                    self.manager.destroy_tunnel(tunnel_name)
        except ValueError:
            print_error("Invalid choice!")
    
    def menu_test_tunnel(self):
        """Test tunnel connectivity menu"""
        print_header("Test Tunnel")
        
        tunnels = self.manager.list_tunnels()
        if not tunnels:
            print_warning("No tunnels found")
            return
        
        for i, tunnel in enumerate(tunnels, 1):
            print(f"{i}. {tunnel['name']} ({tunnel['type'].upper()})")
        
        try:
            choice = int(input(f"{Colors.YELLOW}Select tunnel (1-{len(tunnels)}): {Colors.RESET}"))
            if 1 <= choice <= len(tunnels):
                tunnel_name = tunnels[choice - 1]['name']
                target_ip = input(f"{Colors.YELLOW}Target IP to ping: {Colors.RESET}").strip()
                
                if validate_ip(target_ip):
                    print_info("Testing connectivity...")
                    success, output = self.manager.test_tunnel_connectivity(tunnel_name, target_ip)
                    print(output)
                    
                    if success:
                        print_success("Tunnel connectivity test passed!")
                    else:
                        print_error("Tunnel connectivity test failed!")
                else:
                    print_error("Invalid IP address!")
        except ValueError:
            print_error("Invalid choice!")
    
    def menu_tunnel_status(self):
        """Get tunnel status"""
        print_header("Tunnel Status")
        
        tunnels = self.manager.list_tunnels()
        if not tunnels:
            print_warning("No tunnels found")
            return
        
        for tunnel in tunnels:
            print(f"{Colors.CYAN}{tunnel['name']:<20} {Colors.RESET}", end="")
            if tunnel['status'] == 'active':
                print(f"{Colors.GREEN}{tunnel['status'].upper()}{Colors.RESET}")
            else:
                print(f"{Colors.RED}{tunnel['status'].upper()}{Colors.RESET}")
    
    def menu_export_config(self):
        """Export configuration"""
        print_header("Export Configuration")
        
        filepath = input(f"{Colors.YELLOW}Export to file (default: /tmp/tunnelpeak_backup.json): {Colors.RESET}").strip()
        if not filepath:
            filepath = "/tmp/tunnelpeak_backup.json"
        
        self.manager.export_config(Path(filepath))
    
    def menu_import_config(self):
        """Import configuration"""
        print_header("Import Configuration")
        
        filepath = input(f"{Colors.YELLOW}Import from file: {Colors.RESET}").strip()
        if filepath:
            self.manager.import_config(Path(filepath))
    
    def menu_system_diagnostics(self):
        """Show system diagnostics"""
        print_header("System Diagnostics")
        
        diagnostics = self.manager.get_system_diagnostics()
        
        print(f"{Colors.CYAN}System Information:{Colors.RESET}")
        for key, value in diagnostics['system_info'].items():
            print(f"  {Colors.BOLD}{key.replace('_', ' ').title()}:{Colors.RESET} {value}")
        
        print(f"\n{Colors.CYAN}Tunnel Statistics:{Colors.RESET}")
        print(f"  {Colors.BOLD}Total Tunnels:{Colors.RESET} {diagnostics['tunnels_count']}")
        print(f"  {Colors.BOLD}Active Tunnels:{Colors.RESET} {diagnostics['active_tunnels']}")
