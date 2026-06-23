"""System utility functions"""

import subprocess
import os
import sys
from typing import Tuple, Optional
from pathlib import Path
import ipaddress
import json

from .logger import Colors, print_error, print_warning, print_success, print_info


def check_root():
    """Check if script is run as root"""
    if os.geteuid() != 0:
        print_error("This script must be run as root (use: sudo)")
        sys.exit(1)


def run_command(cmd: str, check: bool = True, capture_output: bool = True) -> Tuple[int, str, str]:
    """Execute a shell command safely and return results"""
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if check and process.returncode != 0:
            print_error(f"Command failed: {cmd}")
            if stderr:
                print_error(f"Error: {stderr}")
        
        return process.returncode, stdout or "", stderr or ""
    except Exception as e:
        print_error(f"Error executing command: {e}")
        return 1, "", str(e)


def validate_ip(ip: str) -> bool:
    """Validate IP address format (IPv4 or IPv6)"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def validate_ipv4(ip: str) -> bool:
    """Validate IPv4 address"""
    try:
        obj = ipaddress.ip_address(ip)
        return obj.version == 4
    except ValueError:
        return False


def validate_ipv6(ip: str) -> bool:
    """Validate IPv6 address"""
    try:
        obj = ipaddress.ip_address(ip)
        return obj.version == 6
    except ValueError:
        return False


def validate_subnet(subnet: str) -> bool:
    """Validate IP subnet in CIDR notation"""
    try:
        ipaddress.ip_network(subnet, strict=False)
        return True
    except ValueError:
        return False


def get_opposite_ip(ip: str, increment: int = 1) -> Optional[str]:
    """Calculate opposite IP address for tunneling"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        opposite = ipaddress.ip_address(int(ip_obj) + increment)
        return str(opposite)
    except Exception as e:
        print_error(f"Error calculating opposite IP: {e}")
        return None


def get_network_interfaces() -> list:
    """Get list of network interfaces"""
    ret, stdout, _ = run_command("ip link show | grep '^[0-9]' | awk '{print $2}' | sed 's/:$//'", check=False)
    if ret == 0:
        return [iface.strip() for iface in stdout.strip().split('\n') if iface.strip()]
    return []


def get_interface_ip(interface: str, version: int = 4) -> Optional[str]:
    """Get IP address of a network interface"""
    if version == 4:
        cmd = f"ip -4 addr show {interface} | grep -oP '(?<=inet\\s)\\d+\\.\\d+\\.\\d+\\.\\d+'"
    else:
        cmd = f"ip -6 addr show {interface} | grep -oP '(?<=inet6\\s)([a-f0-9:]+)' | head -1"
    
    ret, stdout, _ = run_command(cmd, check=False)
    if ret == 0:
        ip = stdout.strip().split('\n')[0] if stdout else None
        return ip if ip else None
    return None


def check_interface_exists(interface: str) -> bool:
    """Check if network interface exists"""
    ret, _, _ = run_command(f"ip link show {interface}", check=False)
    return ret == 0


def bring_interface_up(interface: str) -> bool:
    """Bring network interface up"""
    ret, _, _ = run_command(f"ip link set {interface} up")
    return ret == 0


def bring_interface_down(interface: str) -> bool:
    """Bring network interface down"""
    ret, _, _ = run_command(f"ip link set {interface} down")
    return ret == 0


def install_package(package_name: str) -> bool:
    """Install a system package"""
    print_info(f"Installing {package_name}...")
    
    # Try apt first (Debian/Ubuntu)
    ret, _, _ = run_command(f"apt-get update && apt-get install -y {package_name}", check=False)
    if ret == 0:
        return True
    
    # Try yum (RedHat/CentOS)
    ret, _, _ = run_command(f"yum install -y {package_name}", check=False)
    if ret == 0:
        return True
    
    # Try pacman (Arch)
    ret, _, _ = run_command(f"pacman -S --noconfirm {package_name}", check=False)
    if ret == 0:
        return True
    
    print_error(f"Failed to install {package_name}")
    return False


def install_packages(packages: list) -> bool:
    """Install multiple packages"""
    all_success = True
    for package in packages:
        if not install_package(package):
            all_success = False
    return all_success


def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH"""
    ret, _, _ = run_command(f"which {command}", check=False)
    return ret == 0


def get_system_info() -> dict:
    """Get system information"""
    info = {}
    
    # OS
    ret, os_name, _ = run_command("uname -s", check=False)
    info['os'] = os_name.strip() if ret == 0 else "Unknown"
    
    # Kernel
    ret, kernel, _ = run_command("uname -r", check=False)
    info['kernel'] = kernel.strip() if ret == 0 else "Unknown"
    
    # CPU cores
    ret, cpus, _ = run_command("nproc", check=False)
    info['cpu_cores'] = int(cpus.strip()) if ret == 0 else 1
    
    # RAM
    ret, ram, _ = run_command("free -h | grep Mem | awk '{print $2}'", check=False)
    info['ram'] = ram.strip() if ret == 0 else "Unknown"
    
    return info


def create_directory(path: Path) -> bool:
    """Create directory with proper permissions"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print_error(f"Failed to create directory {path}: {e}")
        return False


def write_file(path: Path, content: str, permissions: int = 0o644) -> bool:
    """Write content to file with proper permissions"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        os.chmod(path, permissions)
        return True
    except Exception as e:
        print_error(f"Failed to write file {path}: {e}")
        return False


def read_file(path: Path) -> Optional[str]:
    """Read file content"""
    try:
        return path.read_text()
    except Exception as e:
        print_error(f"Failed to read file {path}: {e}")
        return None


def load_json_config(path: Path) -> Optional[dict]:
    """Load JSON configuration file"""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print_error(f"Failed to load config {path}: {e}")
        return None


def save_json_config(path: Path, data: dict) -> bool:
    """Save configuration to JSON file"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        os.chmod(path, 0o600)
        return True
    except Exception as e:
        print_error(f"Failed to save config {path}: {e}")
        return False
