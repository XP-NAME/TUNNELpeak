# TUNNELpeak - Advanced Network Tunneling Solution

**Version:** 2.0  
**License:** GPL-3.0  
**Author:** XP-NAME

## Overview

TUNNELpeak is a comprehensive, enterprise-grade network tunneling solution that provides unified management and configuration of multiple tunnel types. It combines the best practices of various tunneling technologies with an intuitive interface and advanced security features.

## Supported Tunnel Types

- **EoIP** (Ethernet over IP) - Layer 2 tunneling
- **IPsec** (Internet Protocol Security) - Encrypted communications
- **GRE** (Generic Routing Encapsulation) - Generic tunneling over IPv4
- **GRE6** - GRE over IPv6
- **IPIP** - IP in IP tunneling
- **SIT** (Simple Internet Transition) - IPv6 over IPv4
- **WireGuard** - Modern VPN protocol
- **Geneve** - Network virtualization encapsulation
- **VXLAN** - Virtual Extensible LAN
- **L2TP** (Layer 2 Tunneling Protocol) - Coming soon
- **OpenVPN** - Coming soon

## Features

### Core Features
- ✅ Multi-tunnel management and orchestration
- ✅ Persistent configuration storage (JSON-based)
- ✅ Systemd integration for service management
- ✅ Interactive CLI and command-line interface
- ✅ Real-time tunnel status monitoring
- ✅ Advanced security options (IPsec encryption, PSK)
- ✅ IPv4 and IPv6 support
- ✅ Dynamic MTU configuration
- ✅ Tunnel connectivity testing

### Advanced Features
- ✅ Configuration import/export
- ✅ System diagnostics
- ✅ Automatic tunnel startup on boot
- ✅ Per-tunnel service management
- ✅ Extensible architecture for new tunnel types
- ✅ Comprehensive logging support
- ✅ Error handling and recovery

## Installation

### Prerequisites
- Linux kernel 4.0+ (for tunnel support)
- Python 3.7+
- Root/sudo access
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/XP-NAME/TUNNELpeak.git
cd TUNNELpeak

# Make executable
chmod +x tunnelpeak.py

# Run with sudo
sudo ./tunnelpeak.py -i
```

## Usage

### Interactive Mode

```bash
sudo ./tunnelpeak.py -i
```

This launches the interactive menu where you can:
- Create new tunnels
- List all tunnels
- Start/stop tunnels
- Delete tunnels
- Test connectivity
- View tunnel status
- Export/import configurations
- View system diagnostics

### Command Line Mode

#### Create a GRE Tunnel
```bash
sudo ./tunnelpeak.py create gre 192.168.1.100 192.168.1.200 tun0 --private-ip 10.0.0.1 --mtu 1400
```

#### Create an IPsec Tunnel
```bash
sudo ./tunnelpeak.py create ipsec 192.168.1.100 192.168.1.200 ipsec0 --private-ip 10.1.0.1
```

#### Create a WireGuard Tunnel
```bash
sudo ./tunnelpeak.py create wireguard 192.168.1.100 192.168.1.200 wg0 --private-ip 10.2.0.1
```

#### List All Tunnels
```bash
sudo ./tunnelpeak.py list
```

#### Check Tunnel Status
```bash
sudo ./tunnelpeak.py status
sudo ./tunnelpeak.py status tun0
```

#### Start/Stop Tunnels
```bash
sudo ./tunnelpeak.py start tun0
sudo ./tunnelpeak.py stop tun0
```

#### Test Tunnel Connectivity
```bash
sudo ./tunnelpeak.py test tun0 10.0.0.2
```

#### Delete Tunnel
```bash
sudo ./tunnelpeak.py delete tun0
```

#### Export Configuration
```bash
sudo ./tunnelpeak.py export /path/to/backup.json
```

#### Import Configuration
```bash
sudo ./tunnelpeak.py import /path/to/backup.json
```

## Configuration

### Configuration Directory
```
/etc/tunnelpeak/
├── tunnels.json          # Persistent tunnel configurations
├── logs/                 # Log files
```

### Configuration File Format
```json
{
  "version": "2.0",
  "created": "2026-06-23T...",
  "tunnels": {
    "tun0": {
      "tunnel_type": "gre",
      "interface_name": "tun0",
      "local_ip": "192.168.1.100",
      "remote_ip": "192.168.1.200",
      "private_ip": "10.0.0.1",
      "mtu": 1400
    }
  }
}
```

## Architecture

### Directory Structure
```
TUNNELpeak/
├── tunnelpeak.py          # Main entry point
├── src/
│   ├── __init__.py
│   ├── tunnel_config.py   # Configuration classes
│   ├── tunnel_manager.py  # Core management
│   ├── cli.py            # Interactive interface
│   ├── utils/
│   │   ├── logger.py     # Logging utilities
│   │   └── system.py     # System utilities
│   └── tunnels/
│       ├── base.py       # Base tunnel class
│       ├── eoip.py       # EoIP implementation
│       ├── ipsec.py      # IPsec implementation
│       ├── gre.py        # GRE/GRE6 implementation
│       ├── ipip.py       # IPIP implementation
│       ├── sit.py        # SIT implementation
│       ├── wireguard.py  # WireGuard implementation
│       ├── geneve.py     # Geneve implementation
│       └── vxlan.py      # VXLAN implementation
├── docs/                 # Documentation
└── README.md            # This file
```

## Tunnel Types Details

### GRE Tunneling
Generic Routing Encapsulation provides simple, stateless tunneling over IPv4 or IPv6.

**Advantages:**
- Low overhead
- Stateless
- Supports multicast

**Use Cases:**
- Site-to-site VPNs
- Network extension

### IPsec
Security protocol suite for secured IP communications using encryption and authentication.

**Advantages:**
- Strong encryption
- Authentication
- IPsec standards compliance

**Use Cases:**
- Secure VPNs
- Encrypted communications
- Enterprise deployments

### WireGuard
Modern VPN protocol emphasizing simplicity, speed, and security.

**Advantages:**
- Simple configuration
- Modern cryptography
- High performance
- Small codebase

**Use Cases:**
- Modern VPNs
- Point-to-point connections
- Mesh networks

### VXLAN
Virtual Extensible LAN for network virtualization.

**Advantages:**
- Layer 2 over Layer 3
- VLAN extension
- Multi-tenancy support

**Use Cases:**
- Data center networking
- Cloud infrastructure
- Network virtualization

## Security Considerations

1. **IPsec Encryption**: Use strong pre-shared keys
2. **WireGuard Keys**: Securely manage private keys
3. **Access Control**: Limit tunnel creation to authorized users
4. **Firewall Rules**: Configure proper firewall rules for tunnel traffic
5. **Monitoring**: Regular monitoring of tunnel status

## Performance Tips

1. **MTU Optimization**: Set appropriate MTU for your network
2. **PMTUD**: Enable Path MTU Discovery
3. **TTL Configuration**: Adjust TTL based on network topology
4. **Routing**: Configure proper routing for tunnel traffic

## Troubleshooting

### Tunnel Won't Start
```bash
# Check systemd service
sudo systemctl status tunnelpeak-<interface_name>.service

# View logs
sudo journalctl -u tunnelpeak-<interface_name>.service -n 50

# Check interface
ip link show
```

### No Connectivity
```bash
# Test with ping
sudo ./tunnelpeak.py test <interface> <target_ip>

# Check routing
ip route show

# Check interface configuration
ip addr show <interface>
```

### High Latency
1. Check MTU settings
2. Verify encryption overhead
3. Monitor system resources
4. Check network congestion

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see LICENSE file for details.

## Support

For issues, feature requests, or questions:

1. Check existing issues on GitHub
2. Create a new issue with detailed information
3. Include system information and configuration
4. Provide reproduction steps

## Changelog

### Version 2.0
- Complete rewrite with modular architecture
- Added WireGuard support
- Improved CLI interface
- Added configuration import/export
- Enhanced error handling
- Comprehensive logging

### Version 1.0
- Initial release
- Basic tunnel support
- IPsec and GRE tunnels

## Roadmap

- [ ] L2TP support
- [ ] OpenVPN integration
- [ ] Web dashboard
- [ ] REST API
- [ ] Advanced monitoring
- [ ] Performance optimization
- [ ] Docker containerization
- [ ] Kubernetes integration

## Acknowledgments

Thanks to:
- The Linux networking community
- EoIP/Geneve/VXLAN documentation
- StrongSwan project
- WireGuard team

## Disclaimer

This software is provided "as-is" without warranty. Users are responsible for:
- Network configuration
- Security implications
- Compliance with local regulations
- Proper testing in non-production environments

---

**Made with ❤️ by XP-NAME**
