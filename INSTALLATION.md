"""Comprehensive Installation Guide for TUNNELpeak"""

# TUNNELpeak Installation Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Installation Setup](#pre-installation-setup)
3. [Installation Methods](#installation-methods)
4. [Verification](#verification)
5. [Initial Configuration](#initial-configuration)
6. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

- **OS**: Linux (Ubuntu 18.04+, Debian 10+, CentOS 7+, Fedora 30+)
- **Kernel**: Linux 4.0+ (for tunnel support)
- **Python**: Python 3.7 or higher
- **RAM**: 256 MB minimum
- **Disk Space**: 50 MB
- **Network**: Internet connection for initial setup
- **Privileges**: Root or sudo access

### Recommended Requirements

- **OS**: Ubuntu 20.04 LTS or Debian 11+
- **Kernel**: Linux 5.4+
- **Python**: Python 3.9+
- **RAM**: 512 MB or more
- **Disk Space**: 100 MB
- **CPU**: Dual-core or better
- **Network**: Gigabit Ethernet or faster

### Supported Distributions

- ✅ Ubuntu 18.04, 20.04, 22.04 LTS
- ✅ Debian 9, 10, 11
- ✅ CentOS 7, 8
- ✅ Fedora 30+
- ✅ AlmaLinux 8+
- ✅ Rocky Linux 8+
- ✅ Raspberry Pi OS (Bullseye+)

---

## Pre-Installation Setup

### Update System Packages

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get upgrade -y

# CentOS/RHEL/Fedora
sudo yum update -y

# Fedora 30+
sudo dnf upgrade -y
```

### Install Python and Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get install -y python3 python3-pip python3-venv git
```

#### CentOS/RHEL 7
```bash
sudo yum install -y python3 python3-pip git
```

#### CentOS/RHEL 8+
```bash
sudo dnf install -y python3 python3-pip git
```

#### Fedora
```bash
sudo dnf install -y python3 python3-pip git
```

---

## Installation Methods

### Method 1: Quick Installation (Recommended)

#### Step 1: Clone Repository

```bash
git clone https://github.com/XP-NAME/TUNNELpeak.git
cd TUNNELpeak
```

#### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt  # If requirements.txt exists
```

#### Step 4: Make Executable

```bash
chmod +x tunnelpeak.py
```

#### Step 5: Run Setup

```bash
sudo ./tunnelpeak.py --help
```

---

### Method 2: System-Wide Installation

#### Step 1: Install to System Directories

```bash
# Clone repository
git clone https://github.com/XP-NAME/TUNNELpeak.git
cd TUNNELpeak

# Create system directory
sudo mkdir -p /opt/tunnelpeak

# Copy files
sudo cp -r . /opt/tunnelpeak/

# Set permissions
sudo chmod +x /opt/tunnelpeak/tunnelpeak.py
sudo chown root:root /opt/tunnelpeak -R
```

#### Step 2: Create Symbolic Link

```bash
sudo ln -s /opt/tunnelpeak/tunnelpeak.py /usr/local/bin/tunnelpeak
```

#### Step 3: Verify Installation

```bash
tunnelpeak --version
```

---

### Method 3: Docker Installation

#### Step 1: Build Docker Image

```bash
git clone https://github.com/XP-NAME/TUNNELpeak.git
cd TUNNELpeak
docker build -t tunnelpeak:2.0 .
```

#### Step 2: Run Docker Container

```bash
docker run --rm -it --privileged \
  -v /etc/tunnelpeak:/etc/tunnelpeak \
  tunnelpeak:2.0 -i
```

---

### Method 4: Package Manager Installation

#### Ubuntu/Debian PPA (Coming Soon)

```bash
sudo add-apt-repository ppa:xp-name/tunnelpeak
sudo apt-get update
sudo apt-get install tunnelpeak
```

#### AUR for Arch Linux (Coming Soon)

```bash
yay -S tunnelpeak
# or
git clone https://aur.archlinux.org/tunnelpeak.git
cd tunnelpeak
makepkg -si
```

---

## Verification

### Check Installation

```bash
# Check version
sudo tunnelpeak --version

# Check help
sudo tunnelpeak --help

# Test interactive mode
sudo tunnelpeak -i
```

### Verify Dependencies

```bash
# Check Python version
python3 --version

# Check required commands
which ip
which iptables
which systemctl
```

### Test Basic Functionality

```bash
# List tunnels (should be empty on fresh install)
sudo tunnelpeak list

# Check system info
sudo tunnelpeak --verbose --help
```

---

## Initial Configuration

### Step 1: Create Configuration Directory

```bash
sudo mkdir -p /etc/tunnelpeak
sudo chmod 750 /etc/tunnelpeak
```

### Step 2: Create First Tunnel

#### Interactive Mode

```bash
sudo tunnelpeak -i
# Select: 1 (Create Tunnel)
# Follow the prompts
```

#### Command Line Mode

```bash
# Create a GRE tunnel
sudo tunnelpeak create gre 192.168.1.100 192.168.1.200 tun0 --private-ip 10.0.0.1

# Create a WireGuard tunnel
sudo tunnelpeak create wireguard 192.168.1.100 192.168.1.200 wg0 --private-ip 10.2.0.1
```

### Step 3: Enable Auto-Start

```bash
# Check systemd service
sudo systemctl status tunnelpeak-tun0.service

# Enable service
sudo systemctl enable tunnelpeak-tun0.service

# Start service
sudo systemctl start tunnelpeak-tun0.service
```

---

## Tunnel Setup Examples

### GRE Tunnel Setup

```bash
# Create tunnel
sudo tunnelpeak create gre 192.168.1.100 192.168.1.200 gre0 \
  --private-ip 10.0.0.1 \
  --mtu 1400

# Start tunnel
sudo tunnelpeak start gre0

# Test connectivity
sudo tunnelpeak test gre0 10.0.0.2
```

### IPsec Tunnel Setup

```bash
# Create tunnel with encryption
sudo tunnelpeak create ipsec 192.168.1.100 192.168.1.200 ipsec0 \
  --private-ip 10.1.0.1

# Tunnel will be created with IPsec protection
sudo tunnelpeak start ipsec0
```

### WireGuard VPN Setup

```bash
# Create WireGuard tunnel
sudo tunnelpeak create wireguard 192.168.1.100 192.168.1.200 wg0 \
  --private-ip 10.2.0.1

# Keys will be auto-generated
sudo tunnelpeak start wg0

# Show public key
wg show wg0
```

### Gaming Tunnel Setup

```bash
# Create optimized gaming tunnel
sudo tunnelpeak create gre 192.168.1.100 192.168.1.200 gaming0 \
  --private-ip 10.3.0.1 \
  --mtu 1300

# Optimizations applied automatically:
# - Low latency ToS marking
# - QoS configuration
# - UDP priority for gaming packets

sudo tunnelpeak start gaming0
```

---

## Post-Installation Configuration

### Configure Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow in on tun0
sudo ufw allow in on wg0

# Firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-interface=tun0 --zone=trusted
sudo firewall-cmd --permanent --add-interface=wg0 --zone=trusted
sudo firewall-cmd --reload
```

### Configure Routing

```bash
# Add route through tunnel
sudo ip route add 10.0.0.0/24 dev tun0

# Make it persistent (systemd-networkd)
echo "[Route]
Destination=10.0.0.0/24
Gateway=10.0.0.1" | sudo tee -a /etc/systemd/network/tun0.network
sudo systemctl restart systemd-networkd
```

### Enable IP Forwarding

```bash
# Temporary
sudo sysctl -w net.ipv4.ip_forward=1

# Permanent
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## Troubleshooting Installation

### Issue: Permission Denied

```bash
# Solution: Run with sudo
sudo tunnelpeak -i

# Or add current user to sudo group
sudo usermod -aG sudo $USER
```

### Issue: Command Not Found

```bash
# Check if in PATH
echo $PATH

# Add to PATH
export PATH=$PATH:/usr/local/bin
echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc
```

### Issue: Missing Dependencies

```bash
# Ubuntu/Debian
sudo apt-get install -y iproute2 iptables iputils-ping net-tools

# CentOS/RHEL
sudo yum install -y iproute iptables-utils iputils bind-utils

# For WireGuard
sudo apt-get install -y wireguard wireguard-tools

# For StrongSwan (IPsec)
sudo apt-get install -y strongswan libcharon-extra-plugins
```

### Issue: Kernel Module Not Loaded

```bash
# Load GRE module
sudo modprobe gre

# Load VXLAN module
sudo modprobe vxlan

# Make persistent
echo "gre" | sudo tee -a /etc/modules
```

---

## System Optimization

### For Better Performance

```bash
# Increase network buffer sizes
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728

# Optimize TCP
sudo sysctl -w net.ipv4.tcp_rmem="4096 87380 67108864"
sudo sysctl -w net.ipv4.tcp_wmem="4096 65536 67108864"

# Increase connection tracking
sudo sysctl -w net.netfilter.nf_conntrack_max=262144
```

### For Gaming Latency

```bash
# Low latency TCP settings
sudo sysctl -w net.ipv4.tcp_timestamps=0
sudo sysctl -w net.ipv4.tcp_fastopen=3

# Reduce retransmission timeout
sudo sysctl -w net.ipv4.tcp_syn_retries=2
sudo sysctl -w net.ipv4.tcp_synack_retries=2
```

---

## Uninstallation

### Remove TUNNELpeak

```bash
# Stop all tunnels
sudo tunnelpeak stop

# Remove system-wide installation
sudo rm -rf /opt/tunnelpeak
sudo rm /usr/local/bin/tunnelpeak

# Remove configuration
sudo rm -rf /etc/tunnelpeak

# Remove systemd services
sudo rm -rf /etc/systemd/system/tunnelpeak-*.service
sudo systemctl daemon-reload
```

---

## Support & Help

### Getting Help

```bash
# General help
tunnelpeak --help

# Command-specific help
tunnelpeak create --help
tunnelpeak start --help

# Enable verbose logging
sudo tunnelpeak -i --verbose
```

### Reporting Issues

If you encounter issues, please:

1. Check the logs: `sudo journalctl -u tunnelpeak-<interface>.service`
2. Run diagnostics: `sudo tunnelpeak diagnostics` (if available)
3. Collect system info: `uname -a && cat /etc/os-release`
4. Report on GitHub: https://github.com/XP-NAME/TUNNELpeak/issues

---

## Next Steps

After installation:

1. ✅ Create your first tunnel
2. ✅ Test connectivity
3. ✅ Configure routing if needed
4. ✅ Set up firewall rules
5. ✅ Enable auto-start for important tunnels
6. ✅ Monitor tunnel status regularly

---

## Version Information

**Current Version**: 2.0  
**Last Updated**: 2026-06-23  
**License**: GPL-3.0

For latest information, visit: https://github.com/XP-NAME/TUNNELpeak
