#!/usr/bin/env python3
"""
ESP8266 NodeMCU Flashing Script
Automated script for common ESP8266 operations using esptool.py
Enhanced with better error handling, verification, and user feedback
"""

import subprocess
import sys
import os
import argparse
import time

class ESP8266Flasher:
    def __init__(self, port, baud=115200, flash_size="4MB"):
        self.port = port
        self.baud = baud
        self.flash_size = flash_size
        self.flash_mode = "dout"
        self.flash_freq = "40m"
        self.max_retries = 3
        
        # Flash size mapping
        self.flash_sizes = {
            "1MB": 0x100000,
            "2MB": 0x200000,
            "4MB": 0x400000,
            "8MB": 0x800000,
            "16MB": 0x1000000
        }
    
    def run_command(self, cmd, check=True, retries=0):
        """Run esptool command and return result with retry logic"""
        try:
            print(f"🔄 Running: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
            
            if result.returncode == 0:
                print("✓ Command completed successfully")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                print(f"✗ Command failed with return code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                
                # Retry logic for connection issues
                if retries < self.max_retries and ("timeout" in result.stderr.lower() or "connection" in result.stderr.lower()):
                    print(f"🔄 Retrying... (attempt {retries + 1}/{self.max_retries})")
                    time.sleep(2)
                    return self.run_command(cmd, check, retries + 1)
                
                return False
        except subprocess.CalledProcessError as e:
            print(f"✗ Command failed: {e}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False
        except (OSError, subprocess.SubprocessError) as e:
            print(f"✗ System error: {e}")
            return False
    
    def check_esptool(self):
        """Check if esptool is available"""
        print("🔍 Checking esptool availability...")
        cmd = "python -m esptool version"
        return self.run_command(cmd, check=False)
    
    def get_chip_info(self):
        """Get ESP8266 chip information"""
        print("📋 Getting chip information...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} chip-id"
        return self.run_command(cmd)
    
    def get_flash_id(self):
        """Get flash ID information"""
        print("💾 Getting flash ID...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} flash-id"
        return self.run_command(cmd)
    
    def read_flash(self, output_file, start=0x00000, size=None, progress=True):
        """Read flash memory to binary file"""
        if size is None:
            size = self.flash_sizes.get(self.flash_size, 0x400000)
        
        print(f"📖 Reading flash memory to {output_file}...")
        progress_flag = "--progress" if progress else ""
        cmd = f"esptool.py --port {self.port} --baud {self.baud} {progress_flag} read-flash {start:08x} {size:08x} {output_file}"
        return self.run_command(cmd)
    
    def write_flash(self, firmware_file, address=0x00000, verify=True, progress=True, erase_all=False):
        """Write firmware to flash memory with enhanced options"""
        if not os.path.exists(firmware_file):
            print(f"❌ Error: Firmware file {firmware_file} not found!")
            return False
        
        # Check file size
        file_size = os.path.getsize(firmware_file)
        print(f"📁 Firmware file size: {file_size:,} bytes")
        
        max_size = self.flash_sizes.get(self.flash_size, 0x400000)
        if file_size > max_size:
            print(f"⚠️  Warning: File size exceeds {self.flash_size} flash capacity")
            return False
        
        print(f"📝 Writing firmware {firmware_file} to flash...")
        
        # Build command with options
        verify_flag = "--verify" if verify else ""
        progress_flag = "--progress" if progress else ""
        erase_flag = "--erase-all" if erase_all else ""
        
        cmd = f"esptool.py --port {self.port} --baud {self.baud} {progress_flag} write-flash --flash-mode {self.flash_mode} --flash-freq {self.flash_freq} --flash-size {self.flash_size} {verify_flag} {erase_flag} {address:08x} {firmware_file}"
        
        return self.run_command(cmd)
    
    def write_multiple_files(self, files_dict, progress=True):
        """Write multiple firmware files (bootloader, application, SPIFFS, etc.)"""
        print("📝 Writing multiple firmware files...")
        
        for address, file_path in files_dict.items():
            if not os.path.exists(file_path):
                print(f"❌ Error: File {file_path} not found!")
                return False
        
        # Build command for multiple files
        progress_flag = "--progress" if progress else ""
        cmd = f"esptool.py --port {self.port} --baud {self.baud} {progress_flag} write-flash --flash-mode {self.flash_mode} --flash-freq {self.flash_freq} --flash-size {self.flash_size}"
        
        for address, file_path in files_dict.items():
            cmd += f" {address:08x} {file_path}"
        
        return self.run_command(cmd)
    
    def erase_flash(self):
        """Erase entire flash memory"""
        print("🗑️  Erasing flash memory...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} erase-flash"
        return self.run_command(cmd)
    
    def write_arduino_sketch(self, sketch_file, address=0x00000, verify=True):
        """Write Arduino sketch (compiled .bin file)"""
        return self.write_flash(sketch_file, address, verify)
    
    def backup_firmware(self, backup_file="esp8266_backup.bin"):
        """Create a complete backup of current firmware"""
        print(f"💾 Creating firmware backup: {backup_file}")
        return self.read_flash(backup_file)
    
    def verify_flash(self, firmware_file, address=0x00000, size=None):
        """Verify written firmware by reading it back and comparing"""
        print("🔍 Verifying written firmware...")
        
        if size is None:
            size = self.flash_sizes.get(self.flash_size, 0x400000)
        
        # Read back the written firmware
        temp_file = "temp_verification.bin"
        if not self.read_flash(temp_file, address, size, progress=False):
            return False
        
        try:
            # Compare files
            with open(firmware_file, 'rb') as f1, open(temp_file, 'rb') as f2:
                if f1.read() == f2.read():
                    print("✓ Verification successful - firmware matches!")
                    os.remove(temp_file)
                    return True
                else:
                    print("❌ Verification failed - firmware does not match!")
                    os.remove(temp_file)
                    return False
        except (OSError, IOError) as e:
            print(f"❌ Verification error: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False
    
    def get_mac_address(self):
        """Get MAC address of the ESP8266"""
        print("🔍 Getting MAC address...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} read-mac"
        return self.run_command(cmd)
    
    def detect_flash_size(self):
        """Detect the actual flash size of the connected ESP8266"""
        print("🔍 Detecting flash size...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} flash-id"
        return self.run_command(cmd)

def main():
    parser = argparse.ArgumentParser(
        description='ESP8266 NodeMCU Flashing Tool - Enhanced with verification and progress tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get chip information
  python esp8266_flash.py --port COM3 --action info
  
  # Backup current firmware
  python esp8266_flash.py --port COM3 --action backup --file my_backup.bin
  
  # Write firmware with verification
  python esp8266_flash.py --port COM3 --action write --file firmware.bin --verify
  
  # Write multiple files (bootloader + application)
  python esp8266_flash.py --port COM3 --action write_multiple --bootloader boot.bin --app app.bin
  
  # Erase flash memory
  python esp8266_flash.py --port COM3 --action erase
  
  # Detect flash size
  python esp8266_flash.py --port COM3 --action detect_size
        """
    )
    
    parser.add_argument('--port', required=True, help='Serial port (e.g., COM3, /dev/ttyUSB0)')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('--flash-size', default='4MB', choices=['1MB', '2MB', '4MB', '8MB', '16MB'], 
                       help='Flash size (default: 4MB)')
    parser.add_argument('--action', required=True, 
                       choices=['info', 'read', 'write', 'erase', 'backup', 'verify', 'mac', 'flash_id', 'detect_size', 'write_multiple'], 
                       help='Action to perform')
    parser.add_argument('--file', help='File path for read/write operations')
    parser.add_argument('--address', default='0x00000', help='Memory address (hex, default: 0x00000)')
    parser.add_argument('--size', help='Size to read (hex, auto-detected if not specified)')
    parser.add_argument('--verify', action='store_true', help='Verify written firmware (for write operations)')
    parser.add_argument('--no-progress', action='store_true', help='Disable progress bar')
    parser.add_argument('--erase-all', action='store_true', help='Erase entire flash before writing')
    parser.add_argument('--no-verify', action='store_true', help='Skip verification for write operations')
    
    # Multiple file options
    parser.add_argument('--bootloader', help='Bootloader file for write_multiple action')
    parser.add_argument('--app', help='Application file for write_multiple action')
    parser.add_argument('--spiffs', help='SPIFFS file for write_multiple action')
    parser.add_argument('--bootloader-addr', default='0x00000', help='Bootloader address (hex)')
    parser.add_argument('--app-addr', default='0x10000', help='Application address (hex)')
    parser.add_argument('--spiffs-addr', default='0x200000', help='SPIFFS address (hex)')
    
    args = parser.parse_args()
    
    # Convert hex strings to integers
    address = int(args.address, 16)
    size = int(args.size, 16) if args.size else None
    
    print("🚀 ESP8266 NodeMCU Flashing Tool - Enhanced Version")
    print("=" * 60)
    
    flasher = ESP8266Flasher(args.port, args.baud, args.flash_size)
    
    # Check esptool availability first
    if not flasher.check_esptool():
        print("❌ esptool not found! Please install it first:")
        print("   pip install esptool")
        sys.exit(1)
    
    # Determine verification setting
    verify = args.verify and not args.no_verify
    progress = not args.no_progress
    
    try:
        if args.action == 'info':
            print("📋 Getting ESP8266 information...")
            flasher.get_chip_info()
            flasher.get_flash_id()
            flasher.get_mac_address()
            
        elif args.action == 'read':
            if not args.file:
                print("❌ Error: --file required for read operation")
                sys.exit(1)
            print(f"📖 Reading flash memory to {args.file}...")
            success = flasher.read_flash(args.file, address, size, progress)
            if success:
                file_size = os.path.getsize(args.file)
                print(f"✓ Successfully read {file_size:,} bytes to {args.file}")
            else:
                print("❌ Failed to read flash memory")
                sys.exit(1)
                
        elif args.action == 'write':
            if not args.file:
                print("❌ Error: --file required for write operation")
                sys.exit(1)
            print(f"📝 Writing firmware {args.file}...")
            success = flasher.write_flash(args.file, address, verify, progress, args.erase_all)
            if success:
                print("✓ Firmware written successfully!")
                if verify:
                    print("✓ Verification completed successfully!")
            else:
                print("❌ Failed to write firmware")
                sys.exit(1)
                
        elif args.action == 'write_multiple':
            files_dict = {}
            if args.bootloader:
                files_dict[int(args.bootloader_addr, 16)] = args.bootloader
            if args.app:
                files_dict[int(args.app_addr, 16)] = args.app
            if args.spiffs:
                files_dict[int(args.spiffs_addr, 16)] = args.spiffs
            
            if not files_dict:
                print("❌ Error: At least one file required for write_multiple operation")
                sys.exit(1)
            
            print("📝 Writing multiple firmware files...")
            success = flasher.write_multiple_files(files_dict, progress)
            if success:
                print("✓ Multiple files written successfully!")
            else:
                print("❌ Failed to write multiple files")
                sys.exit(1)
                
        elif args.action == 'erase':
            print("🗑️  Erasing flash memory...")
            success = flasher.erase_flash()
            if success:
                print("✓ Flash memory erased successfully!")
            else:
                print("❌ Failed to erase flash memory")
                sys.exit(1)
                
        elif args.action == 'backup':
            backup_file = args.file or "esp8266_backup.bin"
            print(f"💾 Creating firmware backup: {backup_file}")
            success = flasher.backup_firmware(backup_file)
            if success:
                file_size = os.path.getsize(backup_file)
                print(f"✓ Backup created successfully: {file_size:,} bytes")
            else:
                print("❌ Failed to create backup")
                sys.exit(1)
                
        elif args.action == 'verify':
            if not args.file:
                print("❌ Error: --file required for verify operation")
                sys.exit(1)
            print(f"🔍 Verifying firmware: {args.file}")
            success = flasher.verify_flash(args.file, address, size)
            if success:
                print("✓ Verification successful!")
            else:
                print("❌ Verification failed!")
                sys.exit(1)
                
        elif args.action == 'mac':
            flasher.get_mac_address()
            
        elif args.action == 'flash_id':
            flasher.get_flash_id()
            
        elif args.action == 'detect_size':
            flasher.detect_flash_size()
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except (OSError, ValueError) as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    
    print("\n🎉 Operation completed successfully!")

if __name__ == "__main__":
    main()
