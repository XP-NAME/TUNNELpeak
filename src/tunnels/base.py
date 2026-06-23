"""Base tunnel implementation"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple
import logging

from src.tunnel_config import TunnelConfig
from src.utils.system import run_command, write_file, read_file, check_interface_exists
from src.utils.logger import print_error, print_success, print_warning, print_info


class BaseTunnel(ABC):
    """Abstract base class for tunnel implementations"""
    
    def __init__(self, config: TunnelConfig):
        self.config = config
        self.logger = logging.getLogger(f"TunnelPeak.{self.__class__.__name__}")
        self.service_path = Path(f"/etc/systemd/system/tunnelpeak-{config.interface_name}.service")
    
    @abstractmethod
    def create(self) -> bool:
        """Create the tunnel"""
        pass
    
    @abstractmethod
    def destroy(self) -> bool:
        """Destroy the tunnel"""
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """Start the tunnel"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Stop the tunnel"""
        pass
    
    @abstractmethod
    def status(self) -> bool:
        """Check tunnel status"""
        pass
    
    def create_systemd_service(self, exec_start: str, after: str = "network-online.target", 
                               requires: bool = True) -> bool:
        """Create systemd service file"""
        service_content = f"""[Unit]
Description=TUNNELpeak - {self.config.tunnel_type.value.upper()} Tunnel {self.config.interface_name}
Documentation=https://github.com/XP-NAME/TUNNELpeak
After={after}
{f'Requires={after}' if requires else ''}
Wants=network-online.target

[Service]
Type=simple
ExecStart={exec_start}
ExecStop=/bin/bash -c 'ip link set {self.config.interface_name} down 2>/dev/null; exit 0'
ExecReload=/bin/bash -c 'systemctl restart {self.service_path.stem}'
Restart=always
RestartSec=5
StartLimitInterval=300
StartLimitBurst=10
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=10

[Install]
WantedBy=multi-user.target
"""
        
        try:
            self.service_path.parent.mkdir(parents=True, exist_ok=True)
            self.service_path.write_text(service_content)
            return True
        except Exception as e:
            print_error(f"Failed to create systemd service: {e}")
            return False
    
    def enable_service(self) -> bool:
        """Enable systemd service"""
        ret, _, _ = run_command("systemctl daemon-reload")
        if ret != 0:
            return False
        
        ret, _, _ = run_command(f"systemctl enable {self.service_path.stem}.service")
        return ret == 0
    
    def start_service(self) -> bool:
        """Start systemd service"""
        ret, _, _ = run_command(f"systemctl start {self.service_path.stem}.service")
        return ret == 0
    
    def stop_service(self) -> bool:
        """Stop systemd service"""
        ret, _, _ = run_command(f"systemctl stop {self.service_path.stem}.service", check=False)
        return ret == 0
    
    def disable_service(self) -> bool:
        """Disable systemd service"""
        ret, _, _ = run_command(f"systemctl disable {self.service_path.stem}.service", check=False)
        return ret == 0
    
    def remove_service(self) -> bool:
        """Remove systemd service file"""
        try:
            if self.service_path.exists():
                self.service_path.unlink()
            return True
        except Exception as e:
            print_error(f"Failed to remove service file: {e}")
            return False
    
    def configure_interface_ip(self, ip: str, prefix: int = None) -> bool:
        """Configure IP address on tunnel interface"""
        if not ip:
            return True
        
        try:
            # Determine CIDR
            if ':' in ip:  # IPv6
                cidr = prefix or 64
            else:  # IPv4
                cidr = prefix or 24
            
            # Add IP address
            ret, _, _ = run_command(
                f"ip addr add {ip}/{cidr} dev {self.config.interface_name}",
                check=False
            )
            
            if ret != 0:
                print_warning(f"Could not add {ip}/{cidr} (may already exist)")
            
            return True
        except Exception as e:
            print_error(f"Failed to configure IP: {e}")
            return False
    
    def set_mtu(self, mtu: int = None) -> bool:
        """Set MTU on tunnel interface"""
        mtu = mtu or self.config.mtu
        ret, _, _ = run_command(f"ip link set {self.config.interface_name} mtu {mtu}", check=False)
        return ret == 0
    
    def bring_interface_up(self) -> bool:
        """Bring interface up"""
        ret, _, _ = run_command(f"ip link set {self.config.interface_name} up")
        return ret == 0
    
    def bring_interface_down(self) -> bool:
        """Bring interface down"""
        ret, _, _ = run_command(f"ip link set {self.config.interface_name} down", check=False)
        return ret == 0
    
    def check_interface_exists(self) -> bool:
        """Check if interface exists"""
        return check_interface_exists(self.config.interface_name)
    
    def test_connectivity(self, target_ip: str, count: int = 4) -> Tuple[bool, str]:
        """Test tunnel connectivity with ping"""
        ret, stdout, _ = run_command(
            f"ping -c {count} -I {self.config.interface_name} {target_ip}",
            check=False
        )
        return ret == 0, stdout
    
    def get_stats(self) -> dict:
        """Get tunnel interface statistics"""
        ret, stdout, _ = run_command(
            f"ip -s link show {self.config.interface_name}",
            check=False
        )
        
        if ret == 0:
            return {'raw': stdout}
        return {}
