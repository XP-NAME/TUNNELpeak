"""Gaming Tunnel - Optimized for low latency gaming"""

from pathlib import Path
import os

from src.tunnel_config import TunnelConfig
from src.tunnels.base import BaseTunnel
from src.utils.system import run_command, write_file
from src.utils.logger import print_error, print_success, print_info, print_warning


class GamingTunnel(BaseTunnel):
    """Gaming-optimized tunnel with QoS and priority"""
    
    def __init__(self, config: TunnelConfig):
        super().__init__(config)
        self.gaming_priority = 7  # High priority
        self.qos_enabled = True
        self.udp_priority = True  # Prioritize UDP for gaming
    
    def create(self) -> bool:
        """Create gaming tunnel with optimization"""
        print_info(f"Creating Gaming tunnel: {self.config.interface_name}")
        
        # Create tunnel interface based on config type
        if self.config.tunnel_type.value == "gre":
            ret = self._create_gre_tunnel()
        elif self.config.tunnel_type.value == "wireguard":
            ret = self._create_wireguard_tunnel()
        else:
            ret = self._create_generic_tunnel()
        
        if not ret:
            return False
        
        # Apply gaming optimizations
        if not self._apply_gaming_optimizations():
            print_warning("Failed to apply some gaming optimizations")
        
        print_success(f"Gaming tunnel '{self.config.interface_name}' created successfully")
        return True
    
    def _create_gre_tunnel(self) -> bool:
        """Create optimized GRE tunnel for gaming"""
        ret, _, _ = run_command(
            f"ip tunnel add {self.config.interface_name} mode gre "
            f"remote {self.config.remote_ip} "
            f"local {self.config.local_ip} "
            f"ttl {self.config.ttl} "
            f"tos 0x10",  # Low latency ToS
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
        
        # Set aggressive MTU for low latency
        gaming_mtu = min(self.config.mtu, 1300)  # Smaller MTU = lower latency
        if not self.set_mtu(gaming_mtu):
            return False
        
        return True
    
    def _create_wireguard_tunnel(self) -> bool:
        """Create optimized WireGuard tunnel for gaming"""
        from src.tunnels.wireguard import WireGuardTunnel
        wg_tunnel = WireGuardTunnel(self.config)
        return wg_tunnel.create()
    
    def _create_generic_tunnel(self) -> bool:
        """Create generic tunnel"""
        ret, _, _ = run_command(
            f"ip tunnel add {self.config.interface_name} mode {self.config.tunnel_type.value} "
            f"remote {self.config.remote_ip} "
            f"local {self.config.local_ip} "
            f"ttl {self.config.ttl}",
            check=False
        )
        
        if ret != 0:
            return False
        
        if not self.bring_interface_up():
            return False
        
        if self.config.private_ip:
            if not self.configure_interface_ip(self.config.private_ip):
                return False
        
        gaming_mtu = min(self.config.mtu, 1300)
        if not self.set_mtu(gaming_mtu):
            return False
        
        return True
    
    def _apply_gaming_optimizations(self) -> bool:
        """Apply gaming-specific optimizations"""
        success = True
        
        # 1. Enable netfilter conntrack for UDP
        print_info("Configuring conntrack for UDP packets...")
        ret, _, _ = run_command(
            "sysctl -w net.netfilter.nf_conntrack_udp_timeout=30",
            check=False
        )
        if ret != 0:
            print_warning("Could not configure UDP timeout")
            success = False
        
        # 2. Disable TCP timestamps for lower latency
        print_info("Disabling TCP timestamps...")
        ret, _, _ = run_command(
            "sysctl -w net.ipv4.tcp_timestamps=0",
            check=False
        )
        if ret != 0:
            print_warning("Could not disable TCP timestamps")
            success = False
        
        # 3. Enable TCP fast open
        print_info("Enabling TCP Fast Open...")
        ret, _, _ = run_command(
            "sysctl -w net.ipv4.tcp_fastopen=3",
            check=False
        )
        if ret != 0:
            print_warning("Could not enable TCP Fast Open")
            success = False
        
        # 4. Reduce TCP retransmission timeout
        print_info("Optimizing TCP retransmission...")
        ret, _, _ = run_command(
            "sysctl -w net.ipv4.tcp_syn_retries=2",
            check=False
        )
        if ret != 0:
            print_warning("Could not optimize TCP retransmission")
            success = False
        
        # 5. Increase buffer sizes
        print_info("Increasing socket buffer sizes...")
        ret, _, _ = run_command(
            "sysctl -w net.core.rmem_max=134217728 net.core.wmem_max=134217728",
            check=False
        )
        if ret != 0:
            print_warning("Could not increase buffer sizes")
            success = False
        
        # 6. Apply QoS rules if enabled
        if self.qos_enabled:
            if not self._setup_qos():
                print_warning("Could not setup QoS")
                success = False
        
        # 7. Configure netfilter rules for UDP priority
        if self.udp_priority:
            if not self._setup_udp_priority():
                print_warning("Could not setup UDP priority")
                success = False
        
        return success
    
    def _setup_qos(self) -> bool:
        """Setup Quality of Service for gaming"""
        print_info("Setting up QoS (Quality of Service)...")
        
        # Add traffic control queue discipline
        ret, _, _ = run_command(
            f"tc qdisc add dev {self.config.interface_name} root "
            f"mqprio num_tc 3 map 2 2 1 0 2 2 2 2 2 2 2 2 2 2 2 2 "
            f"queues 1@0 1@1 2@2 hw 0",
            check=False
        )
        
        if ret != 0:
            # Try simpler approach
            ret, _, _ = run_command(
                f"tc qdisc add dev {self.config.interface_name} root fq_codel",
                check=False
            )
        
        return ret == 0
    
    def _setup_udp_priority(self) -> bool:
        """Setup UDP packet priority for gaming"""
        print_info("Configuring UDP packet priority...")
        
        # Mark UDP packets for gaming ports
        # Common gaming ports: 25000-26000, 27000-27030
        ret1, _, _ = run_command(
            "iptables -t mangle -A OUTPUT -p udp --sport 25000:26000 -j MARK --set-mark 1",
            check=False
        )
        
        ret2, _, _ = run_command(
            "iptables -t mangle -A OUTPUT -p udp --sport 27000:27030 -j MARK --set-mark 1",
            check=False
        )
        
        return ret1 == 0 and ret2 == 0
    
    def destroy(self) -> bool:
        """Destroy gaming tunnel"""
        print_info(f"Destroying Gaming tunnel: {self.config.interface_name}")
        
        # Remove QoS rules
        if self.qos_enabled:
            run_command(
                f"tc qdisc del dev {self.config.interface_name} root",
                check=False
            )
        
        # Remove interface
        ret, _, _ = run_command(
            f"ip tunnel del {self.config.interface_name}",
            check=False
        )
        
        if ret == 0:
            print_success(f"Gaming tunnel '{self.config.interface_name}' destroyed")
            return True
        else:
            print_error(f"Failed to destroy Gaming tunnel")
            return False
    
    def start(self) -> bool:
        """Start gaming tunnel"""
        print_info(f"Starting Gaming tunnel: {self.config.interface_name}")
        return self.bring_interface_up()
    
    def stop(self) -> bool:
        """Stop gaming tunnel"""
        print_info(f"Stopping Gaming tunnel: {self.config.interface_name}")
        return self.bring_interface_down()
    
    def status(self) -> bool:
        """Check gaming tunnel status"""
        return self.check_interface_exists()
    
    def get_latency_info(self) -> dict:
        """Get latency information"""
        ret, output, _ = run_command(
            f"tc class show dev {self.config.interface_name}",
            check=False
        )
        
        return {
            'qdisc_info': output if ret == 0 else None,
            'mtu': self.config.mtu,
            'optimization_level': 'high'
        }
