"""Tunnel configuration and type definitions"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import json
from pathlib import Path


class TunnelType(Enum):
    """Supported tunnel types"""
    EOIP = "eoip"
    IPSEC = "ipsec"
    GRE = "gre"
    GRE6 = "gre6"
    IPIP = "ipip"
    SIT = "sit"
    WIREGUARD = "wireguard"
    GENEVE = "geneve"
    VXLAN = "vxlan"
    L2TP = "l2tp"
    OPENVPN = "openvpn"


class EncryptionMethod(Enum):
    """IPsec encryption methods"""
    AES256_GCM = "aes256gcm16-sha512-ecp384"
    AES256_SHA512 = "aes256-sha512"
    AES128_GCM = "aes128gcm16-sha256-ecp256"
    CHACHA20_POLY = "chacha20poly1305"


@dataclass
class TunnelConfig:
    """Tunnel configuration holder"""
    
    # Basic configuration
    tunnel_type: TunnelType = TunnelType.EOIP
    interface_name: str = "tunnel0"
    description: str = ""
    
    # Network configuration
    local_ip: str = ""
    remote_ip: str = ""
    private_ip: str = ""
    private_ipv6: Optional[str] = None
    gateway_ip: Optional[str] = None
    mtu: int = 1500
    ttl: int = 255
    
    # Security configuration
    preshared_key: str = ""
    enable_encryption: bool = False
    encryption_method: EncryptionMethod = EncryptionMethod.AES256_GCM
    enable_compression: bool = False
    enable_auth: bool = False
    auth_method: str = "sha512"
    
    # Tunnel-specific options
    tunnel_id: int = 1
    key: Optional[int] = None
    flowinfo: int = 0
    
    # Performance tuning
    enable_pmtud: bool = True
    pmtu_discovery: bool = True
    tcp_mss_clamp: int = 1280
    enable_multipath: bool = False
    max_connections: int = 1
    
    # IPv6 configuration
    ipv6_mode: bool = False
    auto_ipv6: bool = False
    ipv6_prefix: str = "fd00::/64"
    
    # Advanced options
    enable_monitoring: bool = True
    enable_routing: bool = False
    routing_table: int = 100
    enable_nat: bool = False
    nat_masquerade: bool = False
    
    # WireGuard specific
    wireguard_private_key: Optional[str] = None
    wireguard_public_key: Optional[str] = None
    wireguard_peerkey: Optional[str] = None
    wireguard_port: int = 51820
    wireguard_keepalive: int = 0
    
    # OpenVPN specific
    openvpn_protocol: str = "udp"
    openvpn_port: int = 1194
    openvpn_cipher: str = "AES-256-GCM"
    openvpn_auth: str = "SHA512"
    
    # Metadata
    enabled: bool = True
    autostart: bool = True
    tags: list = field(default_factory=list)
    custom_options: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'tunnel_type': self.tunnel_type.value,
            'interface_name': self.interface_name,
            'description': self.description,
            'local_ip': self.local_ip,
            'remote_ip': self.remote_ip,
            'private_ip': self.private_ip,
            'private_ipv6': self.private_ipv6,
            'gateway_ip': self.gateway_ip,
            'mtu': self.mtu,
            'ttl': self.ttl,
            'enable_encryption': self.enable_encryption,
            'encryption_method': self.encryption_method.value,
            'enable_compression': self.enable_compression,
            'tunnel_id': self.tunnel_id,
            'ipv6_mode': self.ipv6_mode,
            'enable_monitoring': self.enable_monitoring,
            'autostart': self.autostart,
        }
    
    def to_json(self, filepath: Path) -> None:
        """Save configuration to JSON file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_json(cls, filepath: Path) -> 'TunnelConfig':
        """Load configuration from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Convert string values back to enums
        if 'tunnel_type' in data:
            data['tunnel_type'] = TunnelType(data['tunnel_type'])
        if 'encryption_method' in data:
            data['encryption_method'] = EncryptionMethod(data['encryption_method'])
        
        return cls(**data)
