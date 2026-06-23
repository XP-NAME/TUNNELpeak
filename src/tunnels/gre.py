"""GRE (Generic Routing Encapsulation) tunnel implementation"""

from src.tunnel_config import TunnelConfig
from src.tunnels.base import BaseTunnel
from src.utils.system import run_command
from src.utils.logger import print_error, print_success, print_info


class GRETunnel(BaseTunnel):
    """GRE (Generic Routing Encapsulation) tunnel over IPv4"""
    
    def create(self) -> bool:
        """Create GRE tunnel"""
        print_info(f"Creating GRE tunnel: {self.config.interface_name}")
        
        # Create GRE tunnel interface
        ret, _, _ = run_command(
            f"ip tunnel add {self.config.interface_name} mode gre "
            f"remote {self.config.remote_ip} "
            f"local {self.config.local_ip} "
            f"ttl {self.config.ttl}",
            check=False
        )
        
        if ret != 0:
            print_error("Failed to create GRE tunnel")
            return False
        
        # Configure interface
        if not self.bring_interface_up():
            return False
        
        if self.config.private_ip:
            if not self.configure_interface_ip(self.config.private_ip):
                return False
        
        if not self.set_mtu():
            return False
        
        print_success(f"GRE tunnel '{self.config.interface_name}' created successfully")
        return True
    
    def destroy(self) -> bool:
        """Destroy GRE tunnel"""
        print_info(f"Destroying GRE tunnel: {self.config.interface_name}")
        
        ret, _, _ = run_command(
            f"ip tunnel del {self.config.interface_name}",
            check=False
        )
        
        if ret == 0:
            print_success(f"GRE tunnel '{self.config.interface_name}' destroyed")
            return True
        else:
            print_error(f"Failed to destroy GRE tunnel")
            return False
    
    def start(self) -> bool:
        """Start GRE tunnel"""
        print_info(f"Starting GRE tunnel: {self.config.interface_name}")
        return self.bring_interface_up()
    
    def stop(self) -> bool:
        """Stop GRE tunnel"""
        print_info(f"Stopping GRE tunnel: {self.config.interface_name}")
        return self.bring_interface_down()
    
    def status(self) -> bool:
        """Check GRE tunnel status"""
        return self.check_interface_exists()


class GRE6Tunnel(BaseTunnel):
    """GRE (Generic Routing Encapsulation) tunnel over IPv6"""
    
    def create(self) -> bool:
        """Create GRE6 tunnel"""
        print_info(f"Creating GRE6 tunnel: {self.config.interface_name}")
        
        # Create GRE6 tunnel interface
        ret, _, _ = run_command(
            f"ip tunnel add {self.config.interface_name} mode ip6gre "
            f"remote {self.config.remote_ip} "
            f"local {self.config.local_ip}",
            check=False
        )
        
        if ret != 0:
            print_error("Failed to create GRE6 tunnel")
            return False
        
        # Configure interface
        if not self.bring_interface_up():
            return False
        
        if self.config.private_ipv6:
            if not self.configure_interface_ip(self.config.private_ipv6, prefix=64):
                return False
        
        if not self.set_mtu():
            return False
        
        print_success(f"GRE6 tunnel '{self.config.interface_name}' created successfully")
        return True
    
    def destroy(self) -> bool:
        """Destroy GRE6 tunnel"""
        print_info(f"Destroying GRE6 tunnel: {self.config.interface_name}")
        
        ret, _, _ = run_command(
            f"ip tunnel del {self.config.interface_name}",
            check=False
        )
        
        if ret == 0:
            print_success(f"GRE6 tunnel '{self.config.interface_name}' destroyed")
            return True
        else:
            print_error(f"Failed to destroy GRE6 tunnel")
            return False
    
    def start(self) -> bool:
        """Start GRE6 tunnel"""
        print_info(f"Starting GRE6 tunnel: {self.config.interface_name}")
        return self.bring_interface_up()
    
    def stop(self) -> bool:
        """Stop GRE6 tunnel"""
        print_info(f"Stopping GRE6 tunnel: {self.config.interface_name}")
        return self.bring_interface_down()
    
    def status(self) -> bool:
        """Check GRE6 tunnel status"""
        return self.check_interface_exists()
