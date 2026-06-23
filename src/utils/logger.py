"""Logging utility"""

import logging
import sys
from pathlib import Path
from typing import Optional


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    
    COLORS = {
        logging.DEBUG: Colors.BLUE,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.MAGENTA,
    }
    
    def format(self, record):
        levelname = record.levelname
        if record.levelno in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelno]}{levelname}{Colors.RESET}"
        return super().format(record)


def setup_logger(name: str, log_file: Optional[Path] = None, level=logging.INFO) -> logging.Logger:
    """Setup logger with console and file handlers"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        f'{Colors.DIM}[%(asctime)s]{Colors.RESET} {Colors.CYAN}%(name)s{Colors.RESET} - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def print_banner():
    """Print application banner"""
    banner = f"""
{Colors.BOLD}{Colors.GREEN}
    ████████╗██╗   ██╗███╗   ██╗███╗   ██╗███████╗██╗     ██████╗ ███████╗ █████╗ ██╗  ██╗
    ╚══██╔══╝██║   ██║████╗  ██║████╗  ██║██╔════╝██║     ██╔══██╗██╔════╝██╔══██╗██║ ██╔╝
       ██║   ██║   ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██║     ██████╔╝█████╗  ███████║█████╔╝ 
       ██║   ██║   ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══██║██╔═██╗ 
       ██║   ╚██████╔╝██║ ╚████║██║ ╚████║███████╗███████╗██║     ███████╗██║  ██║██║  ██╗
       ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝���══════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
{Colors.RESET}
{Colors.YELLOW}{Colors.BOLD}                    Advanced Network Tunneling Solution v2.0
                         Secure & Reliable Tunneling{Colors.RESET}
"""
    print(banner)


def print_separator(char: str = '=', length: int = 70):
    """Print separator line"""
    print(f"{Colors.CYAN}{char * length}{Colors.RESET}")


def print_header(text: str):
    """Print styled header"""
    print_separator()
    print(f"{Colors.BOLD}{Colors.YELLOW}{text:^70}{Colors.RESET}")
    print_separator()


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}[+] {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}[!] {message}{Colors.RESET}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}[*] {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}[i] {message}{Colors.RESET}")
