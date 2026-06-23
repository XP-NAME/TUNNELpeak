# Tunnel Methods Comparison & Technical Guide

## Overview

This guide provides detailed technical information about each tunnel type supported by TUNNELpeak, including use cases, advantages, disadvantages, and performance characteristics.

---

## 1. EoIP (Ethernet over IP)

### Technical Details

- **OSI Layer**: Layer 2 (Data Link)
- **Protocol**: RFC 3378
- **Encapsulation**: Ethernet frames over IP
- **Standard Port**: None (IP protocol 97)
- **Encryption**: None (use IPsec for security)

### Advantages

✅ Layer 2 connectivity (bridge networks)  
✅ Supports multicast and broadcast  
✅ Simple to configure  
✅ Low overhead  
✅ Good for extending LANs  

### Disadvantages

❌ No built-in encryption  
❌ Not standardized (MikroTik specific origin)  
❌ Requires custom implementations  
❌ Higher bandwidth consumption (broadcasts)  

### Performance

- **Latency**: 1-2ms (minimal overhead)
- **Throughput**: Near wire speed (90-95%)
- **MTU**: 1500 bytes typical
- **Overhead**: ~20 bytes per frame

### Use Cases

- Network extension across WAN
- LAN bridging
- VLAN extension
- Geographic network clustering

### Example Configuration

```bash
sudo tunnelpeak create eoip 192.168.1.100 192.168.1.200 eoip0 \
  --tunnel-id 1 \
  --mtu 1500
```

### Supported Features in TUNNELpeak

- IPv4 and IPv6 endpoints
- Tunnel ID configuration
- MTU adjustment
- Systemd service integration
- Auto-start on boot

---

## 2. IPsec (Internet Protocol Security)

### Technical Details

- **OSI Layer**: Layer 3 (Network) - Transport
- **Standards**: RFC 4301, 4302, 4303
- **Modes**: Tunnel and Transport
- **Encryption**: AES-128, AES-256, ChaCha20-Poly1305
- **Authentication**: SHA-256, SHA-512, HMAC
- **Key Exchange**: IKEv2 (RFC 7539)
- **Standard Port**: UDP 500 (IKE), UDP 4500 (NAT-T)

### Advantages

✅ Military-grade encryption  
✅ End-to-end security  
✅ Industry standard (RFC)  
✅ Perfect Forward Secrecy (PFS)  
✅ Strong authentication  
✅ Transparent to applications  
✅ Firewall friendly  

### Disadvantages

❌ Complex configuration  
❌ High CPU usage (encryption/decryption)  
❌ Higher latency (15-20ms vs 1-2ms)  
❌ Larger overhead (~80+ bytes)  
❌ NAT traversal issues  
❌ Key management overhead  

### Performance

- **Latency**: 10-20ms (encryption overhead)
- **Throughput**: 60-80% of wire speed
- **MTU**: 1280-1300 bytes (accounting for headers)
- **Overhead**: ~73 bytes (IPv4 + ESP header)
- **CPU Usage**: High (due to encryption)

### Security Parameters

**TUNNELpeak Default Configuration:**
```
IKE Encryption: AES-256-GCM
IKE Integrity: SHA-512
IKE DH Group: ECP-384
ESP Encryption: AES-256-GCM
ESP Integrity: SHA-512
Key Lifetime: 1 hour
DPD (Dead Peer Detection): 30 seconds
```

### Use Cases

- Site-to-site VPNs (enterprise)
- Secure remote access
- End-to-end encryption
- Compliance with security standards
- Financial/healthcare networks

### Example Configuration

```bash
sudo tunnelpeak create ipsec 192.168.1.100 192.168.1.200 ipsec0 \
  --private-ip 10.1.0.1 \
  --enable-encryption
```

### Supported Features in TUNNELpeak

- IKEv2 key exchange
- Multiple encryption algorithms
- PSK and certificate authentication
- DPD support
- Automatic key rotation
- Systemd integration

---

## 3. GRE (Generic Routing Encapsulation)

### Technical Details

- **OSI Layer**: Layer 3 (Network)
- **Standard**: RFC 2784, RFC 2890
- **Protocol Number**: 47
- **Encryption**: None (optional IPsec overlay)
- **Header Size**: 20 bytes (minimum)

### Variants

**GRE over IPv4**
- Standard GRE encapsulation
- IPv4 endpoints
- Widely supported

**GRE6 (GRE over IPv6)**
- IPv6 endpoints
- Modern networks
- Future-proof

### Advantages

✅ Low overhead (20 bytes header)  
✅ Fast processing  
✅ Stateless  
✅ Multicast support  
✅ Simple implementation  
✅ Good for diverse protocols  
✅ Firewall NAT-friendly  

### Disadvantages

❌ No encryption  
❌ No authentication  
❌ Larger MTU reduction  
❌ DoS vulnerable  
✅ Can be mitigated with firewall rules  

### Performance

- **Latency**: 1-3ms
- **Throughput**: 85-95% of wire speed
- **MTU**: 1476 bytes (with standard 1500 MTU)
- **Overhead**: 20 bytes (GRE header) + 20 bytes (IP header)
- **CPU Usage**: Very low

### Use Cases

- Site-to-site connectivity
- Network extension
- Lab/test environments
- High-throughput tunneling
- ISP point-to-point
- Multicast routing

### Example Configuration

```bash
# Standard GRE
sudo tunnelpeak create gre 192.168.1.100 192.168.1.200 gre0 \
  --private-ip 10.0.0.1 \
  --mtu 1400

# GRE6 (IPv6)
sudo tunnelpeak create gre6 2001:db8::1 2001:db8::2 gre60 \
  --private-ipv6 fd00::1/64
```

### Supported Features in TUNNELpeak

- IPv4 and IPv6 support
- PMTUD (Path MTU Discovery)
- TTL configuration
- ToS (Type of Service) marking
- QoS integration

---

## 4. IPIP (IP in IP)

### Technical Details

- **OSI Layer**: Layer 3 (Network)
- **Standard**: RFC 2003
- **Protocol Number**: 4
- **Encryption**: None
- **Header Size**: 20 bytes

### Advantages

✅ Minimal overhead  
✅ Very simple  
✅ Good for IPv4 over IPv4  
✅ Fast processing  
✅ Low CPU usage  

### Disadvantages

❌ No encryption  
❌ Limited protocol support  
❌ No multicast  
❌ Less flexible than GRE  

### Performance

- **Latency**: 1-2ms
- **Throughput**: 90-95% wire speed
- **MTU**: 1480 bytes
- **Overhead**: 20 bytes
- **CPU Usage**: Minimal

### Use Cases

- Simple IP tunneling
- Legacy systems
- VPN aggregation
- Lightweight tunneling

### Example Configuration

```bash
sudo tunnelpeak create ipip 192.168.1.100 192.168.1.200 ipip0 \
  --private-ip 10.0.0.1
```

---

## 5. SIT (Simple Internet Transition)

### Technical Details

- **OSI Layer**: Layer 3 (Network)
- **Standard**: RFC 4214
- **Protocol Number**: 41
- **Purpose**: IPv6 over IPv4
- **Encryption**: None

### Advantages

✅ IPv6 connectivity over IPv4  
✅ Low overhead  
✅ Standardized  
✅ Auto-tunneling support  

### Disadvantages

❌ Specific use case (IPv6 only)  
❌ No encryption  
❌ Limited authentication  

### Use Cases

- IPv6 transition
- 6to4 tunneling
- IPv6 in pure IPv4 networks
- Legacy IPv4 networks

### Example Configuration

```bash
sudo tunnelpeak create sit 192.168.1.100 192.168.1.200 sit0 \
  --private-ipv6 2001:db8::1/64
```

---

## 6. WireGuard

### Technical Details

- **OSI Layer**: Layer 3 (Network)
- **Standard**: Modern cryptographic standards
- **Protocol**: Custom (UDP-based)
- **Port**: 51820 (default, configurable)
- **Encryption**: ChaCha20-Poly1305
- **Hashing**: BLAKE2
- **DH**: Curve25519
- **Lines of Code**: ~4,000 (vs 400,000+ for IPsec)

### Advantages

✅ Modern cryptography  
✅ Simple configuration (key exchange)  
✅ Fast (user-space implementation)  
✅ Low latency (5-8ms typical)  
✅ Mobile-friendly (roaming support)  
✅ Small codebase (auditable)  
✅ Good performance  
✅ Automatic key rotation  
✅ UDP-based (NAT friendly)  

### Disadvantages

❌ Relatively new (adoption ongoing)  
❌ Limited certificate support  
❌ No built-in PKI  
❌ Port binding fixed  

### Performance

- **Latency**: 4-8ms (very good)
- **Throughput**: 85-95% wire speed
- **MTU**: 1420 bytes
- **Overhead**: ~60 bytes
- **CPU Usage**: Low-Medium

### Cryptography

```
Symmetric: ChaCha20-Poly1305
DH: Curve25519
Hash: BLAKE2
Key Size: 256-bit
```

### Use Cases

- Modern VPN deployments
- Mobile VPN (roaming)
- IoT device connections
- Point-to-point VPN
- Mesh networks
- Starlink (native support)

### Example Configuration

```bash
sudo tunnelpeak create wireguard 192.168.1.100 192.168.1.200 wg0 \
  --private-ip 10.2.0.1 \
  --wireguard-port 51820
```

### Supported Features in TUNNELpeak

- Automatic key generation
- Persistent keys storage
- Peer management
- Roaming support
- Perfect Forward Secrecy
- Systemd integration

---

## 7. Geneve (Generic Network Virtualization Encapsulation)

### Technical Details

- **OSI Layer**: Layer 2/3 (Overlay)
- **Standard**: RFC 8926
- **Protocol**: UDP 6081 (default)
- **Encryption**: None (use with IPsec)
- **Header Size**: 8+ bytes

### Advantages

✅ Flexible header (options support)  
✅ Stateless  
✅ Metadata support  
✅ Modern design  
✅ Cloud-native  

### Disadvantages

❌ Newer (less adoption)  
❌ More complex than VXLAN  
❌ Higher overhead potential  

### Use Cases

- Cloud overlays (OpenStack)
- Network virtualization
- Hybrid cloud
- NFV (Network Function Virtualization)

### Example Configuration

```bash
sudo tunnelpeak create geneve 192.168.1.100 192.168.1.200 geneve0 \
  --tunnel-id 1 \
  --private-ip 10.0.0.1
```

---

## 8. VXLAN (Virtual Extensible LAN)

### Technical Details

- **OSI Layer**: Layer 2 (Data Link)
- **Standard**: RFC 7348
- **Protocol**: UDP 4789
- **Encryption**: None (use with IPsec/Wireguard)
- **VLAN Extension**: Supports 16 million vs 4094 VLANs
- **Header Size**: 50 bytes

### Advantages

✅ Extends VLAN capabilities  
✅ Layer 2 overlay  
✅ Multicast support  
✅ Data center standard  
✅ Dynamic MAC learning  

### Disadvantages

❌ Higher overhead (50 bytes)  
❌ Multicast dependency  
❌ No encryption by default  

### Performance

- **Latency**: 2-5ms
- **Throughput**: 80-90% wire speed
- **MTU**: 1450 bytes (considering 50-byte header)
- **Overhead**: 50 bytes

### Use Cases

- Data center virtualization
- Cloud deployments
- VM migration
- Multi-tenancy
- Network segmentation

### Example Configuration

```bash
sudo tunnelpeak create vxlan 192.168.1.100 192.168.1.200 vxlan0 \
  --tunnel-id 100 \
  --private-ip 10.0.0.1
```

---

## 9. Gaming Tunnel (Custom Optimization)

### Technical Details

- **Base Protocol**: GRE/WireGuard
- **Optimization Focus**: Low latency, UDP priority
- **QoS Integration**: Yes
- **Target MTU**: 1300 bytes (optimal for gaming)

### Optimizations Included

✅ Low latency ToS marking  
✅ UDP packet prioritization  
✅ Gaming port detection (25000-27030)  
✅ QoS queue discipline  
✅ Connection tracking optimization  
✅ TCP Fast Open  
✅ Disabled TCP timestamps  
✅ Reduced retransmission timeout  

### Latency Reduction

**Typical Improvements:**
- Jitter: -30% to -50%
- Ping: -5% to -20%
- Packet loss: -10% to -40%

### Performance

- **Target Latency**: <20ms
- **Jitter**: <5ms
- **Packet Loss**: <1%

### Gaming Ports Priority

```
SourcePort 25000-26000  (Various games)
SourcePort 27000-27030  (Steam)
UDP Protocol Priority:   Highest
```

### Use Cases

- Competitive gaming
- Streaming
- Real-time applications
- VoIP optimization
- Latency-sensitive services

### Example Configuration

```bash
# Gaming tunnel with automatic optimizations
sudo tunnelpeak create gre 192.168.1.100 192.168.1.200 gaming0 \
  --private-ip 10.3.0.1 \
  --mtu 1300  # Optimized for gaming

# All gaming optimizations applied automatically:
# - Low latency ToS
# - QoS enabled
# - UDP priority
```

---

## Comparison Table

| Feature | EoIP | IPsec | GRE | IPIP | SIT | WireGuard | Geneve | VXLAN | Gaming |
|---------|------|-------|-----|------|-----|-----------|--------|-------|--------|
| **Layer** | 2 | 3/T | 3 | 3 | 3 | 3 | 2/3 | 2 | 3 |
| **Encryption** | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Latency** | Very Low | High | Very Low | Very Low | Very Low | Low | Low | Low | Ultra-Low |
| **Throughput** | 90-95% | 60-80% | 85-95% | 90-95% | 90-95% | 85-95% | 80-90% | 80-90% | 85-95% |
| **MTU** | 1500 | 1280 | 1476 | 1480 | 1480 | 1420 | 1450 | 1450 | 1300 |
| **Overhead** | 20 | 73+ | 40 | 20 | 20 | 60 | 8+ | 50 | 40 |
| **Complexity** | Low | High | Low | Very Low | Low | Low | Medium | Medium | Medium |
| **Multicast** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **Standards** | Custom | RFC 4301 | RFC 2784 | RFC 2003 | RFC 4214 | Modern | RFC 8926 | RFC 7348 | Custom |

---

## Selection Guide

### Choose Based on Your Needs:

**Need encryption?**
- → IPsec (enterprise) or WireGuard (modern)

**Need multicast?**
- → GRE, Geneve, or VXLAN

**Need performance?**
- → GRE, IPIP, or Gaming Tunnel

**Need simplicity?**
- → IPIP or WireGuard

**Need Layer 2?**
- → EoIP, Geneve, or VXLAN

**Need IPv6?**
- → SIT, GRE6, or WireGuard

**Need lowest latency (gaming)?**
- → Gaming Tunnel (optimized GRE/WireGuard)

**Enterprise use?**
- → IPsec or WireGuard

**Cloud/datacenter?**
- → VXLAN or Geneve

---

## Conclusion

Each tunnel type has specific strengths. TUNNELpeak provides unified management of all these technologies, allowing you to choose the best tool for each use case.

For most modern deployments, **WireGuard** offers the best balance of security, performance, and ease of use. For latency-critical applications like gaming, use the **Gaming Tunnel** optimization.
