"""SIT (Simple Internet Transition) tunnel implementation"""

from src.tunnel_config import TunnelConfig
from src.tunnels.base import BaseTunnel
from src.utils.system import run_command
from src.utils.logger import print_error, print_success, print_info


class SITTunnel(BaseTunnel):
    """SIT (Simple Internet Transition) IPv6 over IPv4 tunnel"""
    
    def create(self) -> bool:
        """Create SIT tunnel"""
        print_info(f"Creating SIT tunnel: {self.config.interface_name}")
        
        # Create SIT tunnel interface
        ret, _, _ = run_command(
            f"ip tunnel add {self.config.interface_name} mode sit "
            f"remote {self.config.remote_ip} "
            f"local {self.config.local_ip} "
            f"ttl {self.config.ttl}",
            check=False
        )
        
        if ret != 0:
            print_error("Failed to create SIT tunnel")
            return False
        
        # Configure interface
        if not self.bring_interface_up():
            return False
        
        # SIT typically uses IPv6
        if self.config.private_ipv6:
            if not self.configure_interface_ip(self.config.private_ipv6, prefix=64):
                return False
        elif self.config.private_ip:
            if not self.configure_interface_ip(self.config.private_ip):
                return False
        
        if not self.set_mtu():
            return False
        
        print_success(f"SIT tunnel '{self.config.interface_name}' created successfully")
        return True
    
    def destroy(self) -> bool:
        """Destroy SIT tunnel"""
        print_info(f"Destroying SIT tunnel: {self.config.interface_name}")
        
        ret, _, _ = run_command(
            f"ip tunnel del {self.config.interface_name}",
            check=False
        )
        
        if ret == 0:
            print_success(f"SIT tunnel '{self.config.interface_name}' destroyed")
            return True
        else:
            print_error(f"Failed to destroy SIT tunnel")
            return False
    
    def start(self) -> bool:
        """Start SIT tunnel"""
        print_info(f"Starting SIT tunnel: {self.config.interface_name}")
        return self.bring_interface_up()
    
    def stop(self) -> bool:
        """Stop SIT tunnel"""
        print_info(f"Stopping SIT tunnel: {self.config.interface_name}")
        return self.bring_interface_down()
    
    def status(self) -> bool:
        """Check SIT tunnel status"""
        return self.check_interface_exists()
