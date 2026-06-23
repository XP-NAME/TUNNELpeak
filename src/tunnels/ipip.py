"""IPIP tunnel implementation"""

from src.tunnel_config import TunnelConfig
from src.tunnels.base import BaseTunnel
from src.utils.system import run_command
from src.utils.logger import print_error, print_success, print_info


class IPIPTunnel(BaseTunnel):
    """IP in IP tunnel implementation"""
    
    def create(self) -> bool:
        """Create IPIP tunnel"""
        print_info(f"Creating IPIP tunnel: {self.config.interface_name}")
        
        # Create IPIP tunnel interface
        ret, _, _ = run_command(
            f"ip tunnel add {self.config.interface_name} mode ipip "
            f"remote {self.config.remote_ip} "
            f"local {self.config.local_ip} "
            f"ttl {self.config.ttl}",
            check=False
        )
        
        if ret != 0:
            print_error("Failed to create IPIP tunnel")
            return False
        
        # Configure interface
        if not self.bring_interface_up():
            return False
        
        if self.config.private_ip:
            if not self.configure_interface_ip(self.config.private_ip):
                return False
        
        if not self.set_mtu():
            return False
        
        print_success(f"IPIP tunnel '{self.config.interface_name}' created successfully")
        return True
    
    def destroy(self) -> bool:
        """Destroy IPIP tunnel"""
        print_info(f"Destroying IPIP tunnel: {self.config.interface_name}")
        
        ret, _, _ = run_command(
            f"ip tunnel del {self.config.interface_name}",
            check=False
        )
        
        if ret == 0:
            print_success(f"IPIP tunnel '{self.config.interface_name}' destroyed")
            return True
        else:
            print_error(f"Failed to destroy IPIP tunnel")
            return False
    
    def start(self) -> bool:
        """Start IPIP tunnel"""
        print_info(f"Starting IPIP tunnel: {self.config.interface_name}")
        return self.bring_interface_up()
    
    def stop(self) -> bool:
        """Stop IPIP tunnel"""
        print_info(f"Stopping IPIP tunnel: {self.config.interface_name}")
        return self.bring_interface_down()
    
    def status(self) -> bool:
        """Check IPIP tunnel status"""
        return self.check_interface_exists()
