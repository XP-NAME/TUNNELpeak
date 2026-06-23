"""Advanced tunnel manager with multi-tunnel support"""

from pathlib import Path
from typing import Dict, Optional, List, Tuple
import json
from datetime import datetime

from src.tunnel_config import TunnelConfig, TunnelType
from src.tunnels import (
    BaseTunnel, EoIPTunnel, IPsecTunnel, GRETunnel, GRE6Tunnel,
    IPIPTunnel, SITTunnel, WireGuardTunnel, GeneveTunnel, VXLANTunnel
)
from src.utils.system import (
    run_command, check_root, create_directory, write_file,
    load_json_config, save_json_config, get_system_info
)
from src.utils.logger import print_error, print_success, print_warning, print_info


class TunnelManager:
    """Main tunnel management system"""
    
    def __init__(self, config_dir: Path = Path("/etc/tunnelpeak")):
        self.config_dir = config_dir
        self.tunnels: Dict[str, Tuple[TunnelConfig, BaseTunnel]] = {}
        self.config_file = config_dir / "tunnels.json"
        self._load_tunnels()
    
    def _load_tunnels(self):
        """Load tunnel configurations from disk"""
        if not self.config_file.exists():
            return
        
        try:
            config_data = load_json_config(self.config_file)
            if not config_data:
                return
            
            for name, tunnel_data in config_data.get('tunnels', {}).items():
                try:
                    # Reconstruct tunnel config
                    config = TunnelConfig(
                        tunnel_type=TunnelType(tunnel_data['tunnel_type']),
                        interface_name=tunnel_data.get('interface_name', name),
                        local_ip=tunnel_data.get('local_ip', ''),
                        remote_ip=tunnel_data.get('remote_ip', ''),
                        private_ip=tunnel_data.get('private_ip', ''),
                        private_ipv6=tunnel_data.get('private_ipv6'),
                        mtu=tunnel_data.get('mtu', 1500),
                    )
                    self.tunnels[name] = (config, None)
                except Exception as e:
                    print_warning(f"Failed to load tunnel {name}: {e}")
        except Exception as e:
            print_warning(f"Failed to load tunnel configurations: {e}")
    
    def _save_tunnels(self):
        """Save tunnel configurations to disk"""
        tunnels_data = {}
        for name, (config, _) in self.tunnels.items():
            tunnels_data[name] = config.to_dict()
        
        data = {
            'version': '2.0',
            'created': datetime.now().isoformat(),
            'tunnels': tunnels_data
        }
        
        save_json_config(self.config_file, data)
    
    def _get_tunnel_handler(self, config: TunnelConfig) -> Optional[BaseTunnel]:
        """Get appropriate tunnel handler based on tunnel type"""
        tunnel_map = {
            TunnelType.EOIP: EoIPTunnel,
            TunnelType.IPSEC: IPsecTunnel,
            TunnelType.GRE: GRETunnel,
            TunnelType.GRE6: GRE6Tunnel,
            TunnelType.IPIP: IPIPTunnel,
            TunnelType.SIT: SITTunnel,
            TunnelType.WIREGUARD: WireGuardTunnel,
            TunnelType.GENEVE: GeneveTunnel,
            TunnelType.VXLAN: VXLANTunnel,
        }
        
        handler_class = tunnel_map.get(config.tunnel_type)
        if handler_class:
            return handler_class(config)
        return None
    
    def create_tunnel(self, config: TunnelConfig, name: Optional[str] = None) -> bool:
        """Create a new tunnel"""
        name = name or config.interface_name
        
        if name in self.tunnels:
            print_error(f"Tunnel '{name}' already exists")
            return False
        
        # Get tunnel handler
        handler = self._get_tunnel_handler(config)
        if not handler:
            print_error(f"Unsupported tunnel type: {config.tunnel_type.value}")
            return False
        
        # Create tunnel
        if not handler.create():
            print_error(f"Failed to create tunnel '{name}'")
            return False
        
        # Store tunnel
        self.tunnels[name] = (config, handler)
        self._save_tunnels()
        
        print_success(f"Tunnel '{name}' created and saved")
        self._print_tunnel_info(config)
        return True
    
    def destroy_tunnel(self, name: str) -> bool:
        """Destroy a tunnel"""
        if name not in self.tunnels:
            print_error(f"Tunnel '{name}' not found")
            return False
        
        config, handler = self.tunnels[name]
        
        if handler:
            if not handler.destroy():
                print_error(f"Failed to destroy tunnel '{name}'")
                return False
        
        del self.tunnels[name]
        self._save_tunnels()
        
        print_success(f"Tunnel '{name}' destroyed")
        return True
    
    def start_tunnel(self, name: str) -> bool:
        """Start a tunnel"""
        if name not in self.tunnels:
            print_error(f"Tunnel '{name}' not found")
            return False
        
        config, handler = self.tunnels[name]
        
        if not handler:
            handler = self._get_tunnel_handler(config)
            if not handler:
                print_error(f"Cannot start tunnel '{name}'")
                return False
        
        if handler.start():
            print_success(f"Tunnel '{name}' started")
            return True
        else:
            print_error(f"Failed to start tunnel '{name}'")
            return False
    
    def stop_tunnel(self, name: str) -> bool:
        """Stop a tunnel"""
        if name not in self.tunnels:
            print_error(f"Tunnel '{name}' not found")
            return False
        
        config, handler = self.tunnels[name]
        
        if not handler:
            handler = self._get_tunnel_handler(config)
            if not handler:
                print_error(f"Cannot stop tunnel '{name}'")
                return False
        
        if handler.stop():
            print_success(f"Tunnel '{name}' stopped")
            return True
        else:
            print_error(f"Failed to stop tunnel '{name}'")
            return False
    
    def get_tunnel_status(self, name: str) -> Optional[dict]:
        """Get tunnel status"""
        if name not in self.tunnels:
            return None
        
        config, handler = self.tunnels[name]
        
        if not handler:
            handler = self._get_tunnel_handler(config)
        
        if not handler:
            return None
        
        ret, stats, _ = run_command(f"ip -s link show {config.interface_name}", check=False)
        
        return {
            'name': name,
            'type': config.tunnel_type.value,
            'interface': config.interface_name,
            'status': 'active' if handler.status() else 'inactive',
            'local_ip': config.local_ip,
            'remote_ip': config.remote_ip,
            'private_ip': config.private_ip,
            'mtu': config.mtu,
            'stats_raw': stats if ret == 0 else None
        }
    
    def list_tunnels(self) -> List[dict]:
        """List all tunnels"""
        tunnels = []
        for name in self.tunnels:
            status = self.get_tunnel_status(name)
            if status:
                tunnels.append(status)
        return tunnels
    
    def test_tunnel_connectivity(self, name: str, target_ip: str, count: int = 4) -> Tuple[bool, str]:
        """Test tunnel connectivity"""
        if name not in self.tunnels:
            return False, f"Tunnel '{name}' not found"
        
        config, handler = self.tunnels[name]
        
        if not handler:
            handler = self._get_tunnel_handler(config)
        
        if not handler:
            return False, "Cannot test tunnel"
        
        success, output = handler.test_connectivity(target_ip, count)
        return success, output
    
    def get_tunnel_config(self, name: str) -> Optional[TunnelConfig]:
        """Get tunnel configuration"""
        if name not in self.tunnels:
            return None
        return self.tunnels[name][0]
    
    def update_tunnel_config(self, name: str, config: TunnelConfig) -> bool:
        """Update tunnel configuration"""
        if name not in self.tunnels:
            print_error(f"Tunnel '{name}' not found")
            return False
        
        self.tunnels[name] = (config, self.tunnels[name][1])
        self._save_tunnels()
        print_success(f"Tunnel '{name}' configuration updated")
        return True
    
    def _print_tunnel_info(self, config: TunnelConfig):
        """Print tunnel information"""
        print()
        print_info(f"Tunnel Type: {config.tunnel_type.value.upper()}")
        print_info(f"Interface: {config.interface_name}")
        print_info(f"Local IP: {config.local_ip}")
        print_info(f"Remote IP: {config.remote_ip}")
        if config.private_ip:
            print_info(f"Private IP: {config.private_ip}")
        if config.private_ipv6:
            print_info(f"Private IPv6: {config.private_ipv6}")
        print_info(f"MTU: {config.mtu}")
        if config.enable_encryption:
            print_info(f"Encryption: {config.encryption_method.value}")
        print()
    
    def export_config(self, filepath: Path) -> bool:
        """Export all tunnel configurations to file"""
        try:
            data = {}
            for name, (config, _) in self.tunnels.items():
                data[name] = config.to_dict()
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            print_success(f"Configurations exported to {filepath}")
            return True
        except Exception as e:
            print_error(f"Failed to export configurations: {e}")
            return False
    
    def import_config(self, filepath: Path) -> bool:
        """Import tunnel configurations from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            for name, tunnel_data in data.items():
                try:
                    config = TunnelConfig(
                        tunnel_type=TunnelType(tunnel_data['tunnel_type']),
                        interface_name=tunnel_data.get('interface_name', name),
                        local_ip=tunnel_data.get('local_ip', ''),
                        remote_ip=tunnel_data.get('remote_ip', ''),
                        private_ip=tunnel_data.get('private_ip', ''),
                        private_ipv6=tunnel_data.get('private_ipv6'),
                        mtu=tunnel_data.get('mtu', 1500),
                    )
                    self.tunnels[name] = (config, None)
                except Exception as e:
                    print_warning(f"Failed to import tunnel {name}: {e}")
            
            self._save_tunnels()
            print_success(f"Configurations imported from {filepath}")
            return True
        except Exception as e:
            print_error(f"Failed to import configurations: {e}")
            return False
    
    def get_system_diagnostics(self) -> dict:
        """Get system diagnostics information"""
        return {
            'system_info': get_system_info(),
            'tunnels_count': len(self.tunnels),
            'active_tunnels': sum(1 for _, (_, h) in self.tunnels.items() if h and h.status()),
        }
