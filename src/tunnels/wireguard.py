"""WireGuard tunnel implementation"""

from pathlib import Path
import os

from src.tunnel_config import TunnelConfig
from src.tunnels.base import BaseTunnel
from src.utils.system import run_command, write_file, install_package, check_command_exists
from src.utils.logger import print_error, print_success, print_info, print_warning


class WireGuardTunnel(BaseTunnel):
    """WireGuard VPN tunnel implementation"""
    
    def __init__(self, config: TunnelConfig):
        super().__init__(config)
        self.wg_config_dir = Path("/etc/wireguard")
        self.wg_config_file = self.wg_config_dir / f"{config.interface_name}.conf"
    
    def install_wireguard(self) -> bool:
        """Install WireGuard"""
        print_info("Installing WireGuard...")
        
        if check_command_exists("wg"):
            print_info("WireGuard already installed")
            return True
        
        # Install WireGuard
        ret, _, _ = run_command("apt-get update && apt-get install -y wireguard wireguard-tools", check=False)
        
        if ret != 0:
            print_error("Failed to install WireGuard")
            return False
        
        print_success("WireGuard installed successfully")
        return True
    
    def generate_keys(self) -> tuple:
        """Generate WireGuard key pair"""
        print_info("Generating WireGuard keys...")
        
        # Generate private key
        ret, privkey, _ = run_command("wg genkey", check=False)
        if ret != 0:
            print_error("Failed to generate private key")
            return None, None
        
        privkey = privkey.strip()
        
        # Generate public key
        ret, pubkey, _ = run_command(f"echo '{privkey}' | wg pubkey", check=False)
        if ret != 0:
            print_error("Failed to generate public key")
            return None, None
        
        pubkey = pubkey.strip()
        
        return privkey, pubkey
    
    def create(self) -> bool:
        """Create WireGuard tunnel"""
        print_info(f"Creating WireGuard tunnel: {self.config.interface_name}")
        
        # Install WireGuard
        if not self.install_wireguard():
            return False
        
        # Generate keys if not provided
        if not self.config.wireguard_private_key:
            privkey, pubkey = self.generate_keys()
            if not privkey:
                return False
            self.config.wireguard_private_key = privkey
            self.config.wireguard_public_key = pubkey
        
        # Create configuration
        wg_config = self._generate_wireguard_config()
        
        # Write configuration
        if not write_file(self.wg_config_file, wg_config, permissions=0o600):
            return False
        
        # Bring interface up
        ret, _, _ = run_command(f"ip link add {self.config.interface_name} type wireguard", check=False)
        if ret != 0 and "already exists" not in str(ret):
            print_warning(f"Interface may already exist")
        
        # Load configuration
        ret, _, _ = run_command(f"wg-quick up {self.config.interface_name}", check=False)
        if ret != 0:
            print_error("Failed to bring up WireGuard interface")
            return False
        
        # Configure IP
        if self.config.private_ip:
            self.configure_interface_ip(self.config.private_ip)
        
        if self.config.private_ipv6:
            self.configure_interface_ip(self.config.private_ipv6, prefix=64)
        
        self.set_mtu()
        
        print_success(f"WireGuard tunnel '{self.config.interface_name}' created successfully")
        print_info(f"Public Key: {self.config.wireguard_public_key}")
        
        return True
    
    def _generate_wireguard_config(self) -> str:
        """Generate WireGuard configuration"""
        config = f"""[Interface]
PrivateKey = {self.config.wireguard_private_key}
Address = {self.config.private_ip}/24
ListenPort = {self.config.wireguard_port}
MTU = {self.config.mtu}

"""
        
        if self.config.wireguard_peerkey:
            config += f"""[Peer]
PublicKey = {self.config.wireguard_peerkey}
Endpoint = {self.config.remote_ip}:{self.config.wireguard_port}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = {self.config.wireguard_keepalive}
"""
        
        return config
    
    def destroy(self) -> bool:
        """Destroy WireGuard tunnel"""
        print_info(f"Destroying WireGuard tunnel: {self.config.interface_name}")
        
        ret, _, _ = run_command(f"wg-quick down {self.config.interface_name}", check=False)
        
        if self.wg_config_file.exists():
            self.wg_config_file.unlink()
        
        if ret == 0:
            print_success(f"WireGuard tunnel '{self.config.interface_name}' destroyed")
            return True
        else:
            print_error(f"Failed to destroy WireGuard tunnel")
            return False
    
    def start(self) -> bool:
        """Start WireGuard tunnel"""
        print_info(f"Starting WireGuard tunnel: {self.config.interface_name}")
        ret, _, _ = run_command(f"wg-quick up {self.config.interface_name}", check=False)
        return ret == 0
    
    def stop(self) -> bool:
        """Stop WireGuard tunnel"""
        print_info(f"Stopping WireGuard tunnel: {self.config.interface_name}")
        ret, _, _ = run_command(f"wg-quick down {self.config.interface_name}", check=False)
        return ret == 0
    
    def status(self) -> bool:
        """Check WireGuard tunnel status"""
        ret, _, _ = run_command(f"wg show {self.config.interface_name}", check=False)
        return ret == 0
