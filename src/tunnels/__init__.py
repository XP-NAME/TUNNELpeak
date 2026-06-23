"""Enhanced tunnel implementations with gaming support"""

from .base import BaseTunnel
from .eoip import EoIPTunnel
from .ipsec import IPsecTunnel
from .gre import GRETunnel, GRE6Tunnel
from .ipip import IPIPTunnel
from .sit import SITTunnel
from .wireguard import WireGuardTunnel
from .geneve import GeneveTunnel
from .vxlan import VXLANTunnel
from .gaming import GamingTunnel

__all__ = [
    'BaseTunnel',
    'EoIPTunnel',
    'IPsecTunnel',
    'GRETunnel',
    'GRE6Tunnel',
    'IPIPTunnel',
    'SITTunnel',
    'WireGuardTunnel',
    'GeneveTunnel',
    'VXLANTunnel',
    'GamingTunnel',
]
