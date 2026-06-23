"""Geneve tunnel implementation"""

from src.tunnel_config import TunnelConfig
from src.tunnels.base import BaseTunnel
from src.utils.system import run_command
from src.utils.logger import print_error, print_success, print_info


class GeneveTunnel(BaseTunnel):
    """Geneve (Generic Network Virtualization Encapsulation) tunnel"""
    
    def create(self) -> bool:
        """Create Geneve tunnel"""
        print_info(f"Creating Geneve tunnel: {self.config.interface_name}")
        
        # Create Geneve tunnel
        ret, _, _ = run_command(
            f"ip link add {self.config.interface_name} type geneve "
            f"remote {self.config.remote_ip} "
            f"id {self.config.tunnel_id} "
            f"ttl {self.config.ttl}",
            check=False
        )
        
        if ret != 0:
            print_error("Failed to create Geneve tunnel")
            return False
        
        # Configure interface
        if not self.bring_interface_up():
            return False
        
        if self.config.private_ip:
            if not self.configure_interface_ip(self.config.private_ip):
                return False
        
        if not self.set_mtu():
            return False
        
        print_success(f"Geneve tunnel '{self.config.interface_name}' created successfully")
        return True
    
    def destroy(self) -> bool:
        """Destroy Geneve tunnel"""
        print_info(f"Destroying Geneve tunnel: {self.config.interface_name}")
        
        ret, _, _ = run_command(
            f"ip link del {self.config.interface_name}",
            check=False
        )
        
        if ret == 0:
            print_success(f"Geneve tunnel '{self.config.interface_name}' destroyed")
            return True
        else:
            print_error(f"Failed to destroy Geneve tunnel")
            return False
    
    def start(self) -> bool:
        """Start Geneve tunnel"""
        print_info(f"Starting Geneve tunnel: {self.config.interface_name}")
        return self.bring_interface_up()
    
    def stop(self) -> bool:
        """Stop Geneve tunnel"""
        print_info(f"Stopping Geneve tunnel: {self.config.interface_name}")
        return self.bring_interface_down()
    
    def status(self) -> bool:
        """Check Geneve tunnel status"""
        return self.check_interface_exists()
