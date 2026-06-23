"""TUNNELpeak - Advanced Network Tunneling Solution"""

__version__ = "2.0.0"
__author__ = "XP-NAME"
__license__ = "GPL-3.0"

from .tunnel_manager import TunnelManager
from .tunnel_config import TunnelConfig, TunnelType

__all__ = ['TunnelManager', 'TunnelConfig', 'TunnelType']
