"""EoIP (Ethernet over IP) tunnel implementation"""

from pathlib import Path
from typing import Optional

from src.tunnel_config import TunnelConfig
from src.tunnels.base import BaseTunnel
from src.utils.system import run_command, write_file, install_package, check_command_exists
from src.utils.logger import print_error, print_success, print_warning, print_info


class EoIPTunnel(BaseTunnel):
    """EoIP (Ethernet over IP) tunnel implementation"""
    
    def __init__(self, config: TunnelConfig):
        super().__init__(config)
        self.eoip_bin = "/usr/local/bin/eoip"
        self.eoip_src = Path("/opt/eoip")
    
    def install_eoip_binary(self) -> bool:
        """Install EoIP binary from source"""
        print_info("Installing EoIP binary...")
        
        # Check if already installed
        ret, _, _ = run_command(f"which eoip", check=False)
        if ret == 0:
            print_info("EoIP already installed")
            return True
        
        # Install dependencies
        packages = ["git", "build-essential", "libfuse-dev", "pkg-config"]
        for pkg in packages:
            install_package(pkg)
        
        # Clone and build
        self.eoip_src.mkdir(parents=True, exist_ok=True)
        
        ret, _, _ = run_command(f"git clone https://github.com/miyugundam/eoip.git {self.eoip_src}", check=False)
        if ret != 0:
            print_error("Failed to clone EoIP repository")
            return False
        
        ret, _, _ = run_command(f"cd {self.eoip_src} && make", check=False)
        if ret != 0:
            print_error("Failed to compile EoIP")
            return False
        
        ret, _, _ = run_command(f"cd {self.eoip_src} && make install", check=False)
        if ret != 0:
            print_error("Failed to install EoIP")
            return False
        
        print_success("EoIP installed successfully")
        return True
    
    def create(self) -> bool:
        """Create EoIP tunnel"""
        print_info(f"Creating EoIP tunnel: {self.config.interface_name}")
        
        # Install EoIP if not present
        if not check_command_exists("eoip"):
            if not self.install_eoip_binary():
                return False
        
        # Build EoIP command
        ip_flag = "-6" if self.config.ipv6_mode else "-4"
        
        eoip_args = f"""{ip_flag} {self.config.interface_name} \\
            local {self.config.local_ip} \\
            remote {self.config.remote_ip} \\
            id {self.config.tunnel_id}"""
        
        if self.config.mtu != 1500:
            eoip_args += f" \\ mtu {self.config.mtu}"
        
        # Create systemd service
        exec_start = f"/usr/local/bin/eoip {eoip_args}"
        if not self.create_systemd_service(exec_start):
            return False
        
        # Enable and start service
        if not self.enable_service():
            return False
        
        if not self.start_service():
            return False
        
        # Configure interface
        self.bring_interface_up()
        if self.config.private_ip:
            self.configure_interface_ip(self.config.private_ip)
        if self.config.private_ipv6:
            self.configure_interface_ip(self.config.private_ipv6, prefix=64)
        
        self.set_mtu()
        
        print_success(f"EoIP tunnel '{self.config.interface_name}' created successfully")
        return True
    
    def destroy(self) -> bool:
        """Destroy EoIP tunnel"""
        print_info(f"Destroying EoIP tunnel: {self.config.interface_name}")
        
        self.stop_service()
        self.disable_service()
        self.remove_service()
        
        # Remove interface
        run_command(f"ip link set {self.config.interface_name} down", check=False)
        
        print_success(f"EoIP tunnel '{self.config.interface_name}' destroyed")
        return True
    
    def start(self) -> bool:
        """Start EoIP tunnel"""
        print_info(f"Starting EoIP tunnel: {self.config.interface_name}")
        return self.start_service()
    
    def stop(self) -> bool:
        """Stop EoIP tunnel"""
        print_info(f"Stopping EoIP tunnel: {self.config.interface_name}")
        return self.stop_service()
    
    def status(self) -> bool:
        """Check EoIP tunnel status"""
        ret, _, _ = run_command(
            f"systemctl is-active {self.service_path.stem}.service",
            check=False
        )
        return ret == 0
