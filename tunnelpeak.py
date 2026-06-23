#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TUNNELpeak - Advanced Network Tunneling Solution

Usage:
    tunnelpeak [--interactive] [--help] [--version]
    tunnelpeak create <tunnel_type> <local_ip> <remote_ip> <interface_name>
    tunnelpeak delete <interface_name>
    tunnelpeak start <interface_name>
    tunnelpeak stop <interface_name>
    tunnelpeak status [interface_name]
    tunnelpeak test <interface_name> <target_ip>
    tunnelpeak list
    tunnelpeak export <filepath>
    tunnelpeak import <filepath>
"""

import sys
import os
from pathlib import Path
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli import TunnelPeakCLI
from src.tunnel_manager import TunnelManager
from src.tunnel_config import TunnelConfig, TunnelType
from src.utils.logger import (
    print_banner, print_header, print_error, print_success,
    print_info, print_warning, setup_logger
)
from src.utils.system import check_root, validate_ip


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='TUNNELpeak - Advanced Network Tunneling Solution',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--version', action='version', version='TUNNELpeak 2.0')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Launch interactive menu')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--log', type=str, default=None,
                       help='Log file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create new tunnel')
    create_parser.add_argument('type', choices=[t.value for t in TunnelType],
                              help='Tunnel type')
    create_parser.add_argument('local_ip', help='Local IP address')
    create_parser.add_argument('remote_ip', help='Remote IP address')
    create_parser.add_argument('interface', help='Interface name')
    create_parser.add_argument('--private-ip', default=None, help='Private IP address')
    create_parser.add_argument('--mtu', type=int, default=1500, help='MTU size')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete tunnel')
    delete_parser.add_argument('interface', help='Interface name')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start tunnel')
    start_parser.add_argument('interface', help='Interface name')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop tunnel')
    stop_parser.add_argument('interface', help='Interface name')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check tunnel status')
    status_parser.add_argument('interface', nargs='?', default=None, help='Interface name')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all tunnels')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test tunnel connectivity')
    test_parser.add_argument('interface', help='Interface name')
    test_parser.add_argument('target_ip', help='Target IP to ping')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export configurations')
    export_parser.add_argument('filepath', help='Output file path')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import configurations')
    import_parser.add_argument('filepath', help='Input file path')
    
    args = parser.parse_args()
    
    # Check root
    check_root()
    
    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    log_file = Path(args.log) if args.log else None
    logger = setup_logger('TunnelPeak', log_file)
    
    # Print banner
    if not args.command or args.interactive:
        print_banner()
    
    # Initialize manager
    manager = TunnelManager()
    
    # Handle commands
    if args.command == 'create':
        tunnel_type = TunnelType(args.type)
        
        if not validate_ip(args.local_ip):
            print_error(f"Invalid local IP: {args.local_ip}")
            sys.exit(1)
        
        if not validate_ip(args.remote_ip):
            print_error(f"Invalid remote IP: {args.remote_ip}")
            sys.exit(1)
        
        config = TunnelConfig(
            tunnel_type=tunnel_type,
            interface_name=args.interface,
            local_ip=args.local_ip,
            remote_ip=args.remote_ip,
            private_ip=args.private_ip or '',
            mtu=args.mtu
        )
        
        if manager.create_tunnel(config):
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.command == 'delete':
        if manager.destroy_tunnel(args.interface):
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.command == 'start':
        if manager.start_tunnel(args.interface):
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.command == 'stop':
        if manager.stop_tunnel(args.interface):
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.command == 'status':
        if args.interface:
            status = manager.get_tunnel_status(args.interface)
            if status:
                print_info(f"Status: {status['status']}")
                sys.exit(0)
            else:
                print_error("Tunnel not found")
                sys.exit(1)
        else:
            tunnels = manager.list_tunnels()
            if tunnels:
                print_header("Tunnel Status")
                for tunnel in tunnels:
                    status_str = f"{tunnel['name']}: {tunnel['status']}"
                    print_info(status_str)
                sys.exit(0)
            else:
                print_warning("No tunnels found")
                sys.exit(0)
    
    elif args.command == 'list':
        tunnels = manager.list_tunnels()
        if tunnels:
            print_header("Active Tunnels")
            for tunnel in tunnels:
                print_info(f"{tunnel['name']} ({tunnel['type']}) - {tunnel['status']}")
            sys.exit(0)
        else:
            print_warning("No tunnels found")
            sys.exit(0)
    
    elif args.command == 'test':
        success, output = manager.test_tunnel_connectivity(args.interface, args.target_ip)
        print(output)
        if success:
            print_success("Connectivity test passed!")
            sys.exit(0)
        else:
            print_error("Connectivity test failed!")
            sys.exit(1)
    
    elif args.command == 'export':
        if manager.export_config(Path(args.filepath)):
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.command == 'import':
        if manager.import_config(Path(args.filepath)):
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.interactive or not args.command:
        cli = TunnelPeakCLI()
        try:
            cli.run()
        except KeyboardInterrupt:
            print_warning("\nInterrupted by user")
            sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print_error(f"Fatal error: {e}")
        sys.exit(1)
