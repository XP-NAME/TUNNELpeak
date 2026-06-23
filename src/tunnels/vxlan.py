"""VXLAN tunnel implementation"""

from src.tunnel_config import TunnelConfig
from src.tunnels.base import BaseTunnel
from src.utils.system import run_command
from src.utils.logger import print_error, print_success, print_info


class VXLANTunnel(BaseTunnel):
    """VXLAN (Virtual Extensible LAN) tunnel"""
    
    def create(self) -> bool:
        """Create VXLAN tunnel"""
        print_info(f"Creating VXLAN tunnel: {self.config.interface_name}")
        
        # Create VXLAN tunnel
        ret, _, _ = run_command(
            f"ip link add {self.config.interface_name} type vxlan "
            f"remote {self.config.remote_ip} "
            f"id {self.config.tunnel_id} "
            f"dstport 4789",
            check=False
        )
        
        if ret != 0:
            print_error("Failed to create VXLAN tunnel")
            return False
        
        # Configure interface
        if not self.bring_interface_up():
            return False
        
        if self.config.private_ip:
            if not self.configure_interface_ip(self.config.private_ip):
                return False
        
        if not self.set_mtu():
            return False
        
        print_success(f"VXLAN tunnel '{self.config.interface_name}' created successfully")
        return True
    
    def destroy(self) -> bool:
        """Destroy VXLAN tunnel"""
        print_info(f"Destroying VXLAN tunnel: {self.config.interface_name}")
        
        ret, _, _ = run_command(
            f"ip link del {self.config.interface_name}",
            check=False
        )
        
        if ret == 0:
            print_success(f"VXLAN tunnel '{self.config.interface_name}' destroyed")
            return True
        else:
            print_error(f"Failed to destroy VXLAN tunnel")
            return False
    
    def start(self) -> bool:
        """Start VXLAN tunnel"""
        print_info(f"Starting VXLAN tunnel: {self.config.interface_name}")
        return self.bring_interface_up()
    
    def stop(self) -> bool:
        """Stop VXLAN tunnel"""
        print_info(f"Stopping VXLAN tunnel: {self.config.interface_name}")
        return self.bring_interface_down()
    
    def status(self) -> bool:
        """Check VXLAN tunnel status"""
        return self.check_interface_exists()
