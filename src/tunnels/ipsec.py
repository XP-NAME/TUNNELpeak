"""IPsec tunnel implementation"""

from pathlib import Path
import os

from src.tunnel_config import TunnelConfig, EncryptionMethod
from src.tunnels.base import BaseTunnel
from src.utils.system import run_command, write_file, install_package, get_opposite_ip
from src.utils.logger import print_error, print_success, print_warning, print_info


class IPsecTunnel(BaseTunnel):
    """IPsec tunnel implementation using StrongSwan"""
    
    def __init__(self, config: TunnelConfig):
        super().__init__(config)
        self.ipsec_conf = Path("/etc/ipsec.conf")
        self.ipsec_secrets = Path("/etc/ipsec.secrets")
    
    def install_strongswan(self) -> bool:
        """Install StrongSwan"""
        print_info("Installing StrongSwan...")
        
        packages = [
            "strongswan",
            "strongswan-pki",
            "libcharon-extra-plugins",
            "libcharon-standard-plugins"
        ]
        
        for pkg in packages:
            if not install_package(pkg):
                print_warning(f"Could not install {pkg}")
        
        print_success("StrongSwan installed")
        return True
    
    def create(self) -> bool:
        """Create IPsec tunnel"""
        print_info(f"Creating IPsec tunnel: {self.config.interface_name}")
        
        # Install StrongSwan
        self.install_strongswan()
        
        # Get opposite IP for remote peer
        opposite_ip = get_opposite_ip(self.config.private_ip)
        if not opposite_ip:
            opposite_ip = self.config.remote_ip
        
        # Create IPsec configuration
        ipsec_config = self._generate_ipsec_config(opposite_ip)
        
        # Backup existing config
        if self.ipsec_conf.exists():
            run_command(f"cp {self.ipsec_conf} {self.ipsec_conf}.backup.{self.config.interface_name}")
        
        # Write configuration
        if not write_file(self.ipsec_conf, ipsec_config):
            return False
        
        # Write secrets
        secrets_entry = f"{self.config.private_ip} {opposite_ip} : PSK \"{self.config.preshared_key}\"\n"
        
        if self.ipsec_secrets.exists():
            existing = self.ipsec_secrets.read_text()
            if f"{self.config.private_ip} {opposite_ip}" not in existing:
                self.ipsec_secrets.write_text(existing + secrets_entry)
        else:
            write_file(self.ipsec_secrets, secrets_entry, permissions=0o600)
        
        os.chmod(self.ipsec_secrets, 0o600)
        
        # Create systemd service
        exec_start = "/usr/sbin/ipsec start --nofork"
        if not self.create_systemd_service(exec_start):
            return False
        
        if not self.enable_service():
            return False
        
        if not self.start_service():
            return False
        
        print_success(f"IPsec tunnel '{self.config.interface_name}' created successfully")
        return True
    
    def _generate_ipsec_config(self, opposite_ip: str) -> str:
        """Generate IPsec configuration"""
        encryption = self.config.encryption_method.value
        
        config = f"""config setup
    charondebug=all
    uniqueids=no
    igmpversion=2
    max_threads=16
    max_queued=32

conn {self.config.interface_name}
    description="{self.config.description or self.config.interface_name}"
    
    # Local side
    leftprotoport=tcp/1194
    leftid={self.config.private_ip}
    leftsubnet={self.config.private_ip}/128
    leftfirewall=yes
    leftauth=psk
    
    # Remote side
    right={opposite_ip}
    rightid={opposite_ip}
    rightsubnet={opposite_ip}/128
    rightauth=psk
    
    # IKE and ESP Configuration
    ike={encryption}!
    esp={encryption}!
    
    # Protocol and Key Exchange
    keyexchange=ikev2
    rekey=yes
    rekeymargin=3m
    rekeyfuzz=100%
    
    # Timeout and Retry
    ikelifetime=24h
    lifetime=1h
    keyingtries=%forever
    dpdaction=restart
    dpddelay=30s
    dpdtimeout=120s
    
    # Connection Parameters
    auto=start
    authby=secret
    type=transport
    fragmentation=yes
"""
        return config
    
    def destroy(self) -> bool:
        """Destroy IPsec tunnel"""
        print_info(f"Destroying IPsec tunnel: {self.config.interface_name}")
        
        self.stop_service()
        self.disable_service()
        self.remove_service()
        
        # Remove IPsec secrets entry
        opposite_ip = get_opposite_ip(self.config.private_ip) or self.config.remote_ip
        if self.ipsec_secrets.exists():
            content = self.ipsec_secrets.read_text()
            lines = [line for line in content.split('\n') 
                    if f"{self.config.private_ip} {opposite_ip}" not in line]
            if lines:
                self.ipsec_secrets.write_text('\n'.join(lines))
                os.chmod(self.ipsec_secrets, 0o600)
        
        print_success(f"IPsec tunnel '{self.config.interface_name}' destroyed")
        return True
    
    def start(self) -> bool:
        """Start IPsec tunnel"""
        print_info(f"Starting IPsec tunnel: {self.config.interface_name}")
        ret, _, _ = run_command(f"ipsec up {self.config.interface_name}", check=False)
        return ret == 0
    
    def stop(self) -> bool:
        """Stop IPsec tunnel"""
        print_info(f"Stopping IPsec tunnel: {self.config.interface_name}")
        ret, _, _ = run_command(f"ipsec down {self.config.interface_name}", check=False)
        return ret == 0
    
    def status(self) -> bool:
        """Check IPsec tunnel status"""
        ret, stdout, _ = run_command(
            f"ipsec status {self.config.interface_name}",
            check=False
        )
        return ret == 0 and "established" in stdout.lower()
