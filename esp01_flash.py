#!/usr/bin/env python3
"""
ESP01 Flashing Script
Automated script for ESP01 (1MB flash) operations using esptool.py
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

class ESP01Flasher:
    def __init__(self, port, baud=115200):
        self.port = port
        self.baud = baud
        self.flash_size = "1MB"  # ESP01 typically has 1MB flash
        self.flash_mode = "dio"
        self.flash_freq = "40m"
    
    def run_command(self, cmd):
        """Run esptool command and return result"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return False
            print(result.stdout)
            return True
        except Exception as e:
            print(f"Exception: {e}")
            return False
    
    def get_chip_info(self):
        """Get ESP01 chip information"""
        print("Getting chip information...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} chip_id"
        return self.run_command(cmd)
    
    def read_flash(self, output_file, start=0x00000, size=0x100000):
        """Read flash memory to binary file (1MB for ESP01)"""
        print(f"Reading flash memory to {output_file}...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} read_flash {start:08x} {size:08x} {output_file}"
        return self.run_command(cmd)
    
    def write_flash(self, firmware_file, address=0x00000):
        """Write firmware to flash memory"""
        if not os.path.exists(firmware_file):
            print(f"Error: Firmware file {firmware_file} not found!")
            return False
        
        print(f"Writing firmware {firmware_file} to flash...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} write_flash --flash_mode {self.flash_mode} --flash_freq {self.flash_freq} --flash_size {self.flash_size} {address:08x} {firmware_file}"
        return self.run_command(cmd)
    
    def erase_flash(self):
        """Erase entire flash memory"""
        print("Erasing flash memory...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} erase_flash"
        return self.run_command(cmd)
    
    def write_arduino_sketch(self, sketch_file, address=0x00000):
        """Write Arduino sketch (compiled .bin file)"""
        return self.write_flash(sketch_file, address)
    
    def backup_firmware(self, backup_file="esp01_backup.bin"):
        """Create a complete backup of current firmware"""
        print(f"Creating firmware backup: {backup_file}")
        return self.read_flash(backup_file)
    
    def write_at_firmware(self, at_firmware_file):
        """Write AT firmware to ESP01"""
        print("Writing AT firmware to ESP01...")
        return self.write_flash(at_firmware_file, 0x00000)

def main():
    parser = argparse.ArgumentParser(description='ESP01 Flashing Tool')
    parser.add_argument('--port', required=True, help='Serial port (e.g., COM3, /dev/ttyUSB0)')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('--action', required=True, choices=['info', 'read', 'write', 'erase', 'backup', 'at_firmware'], 
                       help='Action to perform')
    parser.add_argument('--file', help='File path for read/write operations')
    parser.add_argument('--address', default='0x00000', help='Memory address (hex, default: 0x00000)')
    parser.add_argument('--size', default='0x100000', help='Size to read (hex, default: 0x100000 for 1MB)')
    
    args = parser.parse_args()
    
    # Convert hex strings to integers
    address = int(args.address, 16)
    size = int(args.size, 16)
    
    flasher = ESP01Flasher(args.port, args.baud)
    
    if args.action == 'info':
        flasher.get_chip_info()
    elif args.action == 'read':
        if not args.file:
            print("Error: --file required for read operation")
            sys.exit(1)
        flasher.read_flash(args.file, address, size)
    elif args.action == 'write':
        if not args.file:
            print("Error: --file required for write operation")
            sys.exit(1)
        flasher.write_flash(args.file, address)
    elif args.action == 'erase':
        flasher.erase_flash()
    elif args.action == 'backup':
        backup_file = args.file or "esp01_backup.bin"
        flasher.backup_firmware(backup_file)
    elif args.action == 'at_firmware':
        if not args.file:
            print("Error: --file required for AT firmware operation")
            sys.exit(1)
        flasher.write_at_firmware(args.file)

if __name__ == "__main__":
    main()