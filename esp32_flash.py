#!/usr/bin/env python3
"""
ESP32 Flashing Script
Automated script for ESP32 operations using esptool.py
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

class ESP32Flasher:
    def __init__(self, port, baud=115200):
        self.port = port
        self.baud = baud
        self.flash_size = "4MB"
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
        """Get ESP32 chip information"""
        print("Getting chip information...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} chip_id"
        return self.run_command(cmd)
    
    def read_flash(self, output_file, start=0x00000, size=0x400000):
        """Read flash memory to binary file"""
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
    
    def write_complete_firmware(self, bootloader, partition_table, app):
        """Write complete ESP32 firmware (bootloader + partition table + app)"""
        if not all(os.path.exists(f) for f in [bootloader, partition_table, app]):
            print("Error: One or more firmware files not found!")
            return False
        
        print("Writing complete ESP32 firmware...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} write_flash --flash_mode {self.flash_mode} --flash_freq {self.flash_freq} --flash_size {self.flash_size} 0x1000 {bootloader} 0x8000 {partition_table} 0x10000 {app}"
        return self.run_command(cmd)
    
    def erase_flash(self):
        """Erase entire flash memory"""
        print("Erasing flash memory...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} erase_flash"
        return self.run_command(cmd)
    
    def write_arduino_sketch(self, sketch_file, address=0x10000):
        """Write Arduino sketch (compiled .bin file) to app partition"""
        return self.write_flash(sketch_file, address)
    
    def backup_firmware(self, backup_file="esp32_backup.bin"):
        """Create a complete backup of current firmware"""
        print(f"Creating firmware backup: {backup_file}")
        return self.read_flash(backup_file)
    
    def read_partition(self, partition_name, output_file):
        """Read specific partition from flash"""
        # Common ESP32 partition addresses
        partitions = {
            'bootloader': (0x1000, 0x6000),
            'partition_table': (0x8000, 0x1000),
            'app': (0x10000, 0x100000),
            'nvs': (0x9000, 0x6000),
            'otadata': (0xd000, 0x2000),
            'spiffs': (0x180000, 0x200000)
        }
        
        if partition_name not in partitions:
            print(f"Unknown partition: {partition_name}")
            print(f"Available partitions: {', '.join(partitions.keys())}")
            return False
        
        start, size = partitions[partition_name]
        print(f"Reading {partition_name} partition...")
        return self.read_flash(output_file, start, size)

def main():
    parser = argparse.ArgumentParser(description='ESP32 Flashing Tool')
    parser.add_argument('--port', required=True, help='Serial port (e.g., COM3, /dev/ttyUSB0)')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('--action', required=True, 
                       choices=['info', 'read', 'write', 'write_complete', 'erase', 'backup', 'read_partition'], 
                       help='Action to perform')
    parser.add_argument('--file', help='File path for read/write operations')
    parser.add_argument('--bootloader', help='Bootloader file for complete firmware write')
    parser.add_argument('--partition_table', help='Partition table file for complete firmware write')
    parser.add_argument('--app', help='Application file for complete firmware write')
    parser.add_argument('--address', default='0x00000', help='Memory address (hex, default: 0x00000)')
    parser.add_argument('--size', default='0x400000', help='Size to read (hex, default: 0x400000)')
    parser.add_argument('--partition', help='Partition name for read_partition action')
    
    args = parser.parse_args()
    
    # Convert hex strings to integers
    address = int(args.address, 16)
    size = int(args.size, 16)
    
    flasher = ESP32Flasher(args.port, args.baud)
    
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
    elif args.action == 'write_complete':
        if not all([args.bootloader, args.partition_table, args.app]):
            print("Error: --bootloader, --partition_table, and --app required for complete firmware write")
            sys.exit(1)
        flasher.write_complete_firmware(args.bootloader, args.partition_table, args.app)
    elif args.action == 'erase':
        flasher.erase_flash()
    elif args.action == 'backup':
        backup_file = args.file or "esp32_backup.bin"
        flasher.backup_firmware(backup_file)
    elif args.action == 'read_partition':
        if not args.partition or not args.file:
            print("Error: --partition and --file required for read_partition operation")
            sys.exit(1)
        flasher.read_partition(args.partition, args.file)

if __name__ == "__main__":
    main()