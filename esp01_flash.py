#!/usr/bin/env python3
"""
ESP01 Flashing Script
Automated script for ESP01 (1MB flash) operations using esptool.py
Enhanced with better error handling, verification, and user feedback
"""

import subprocess
import sys
import os
import argparse
import time

class ESP01Flasher:
    def __init__(self, port, baud=115200):
        self.port = port
        self.baud = baud
        self.flash_size = "1MB"  # ESP01 typically has 1MB flash
        self.flash_mode = "dio"
        self.flash_freq = "40m"
        self.max_retries = 3
    
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
        """Get ESP01 chip information"""
        print("📋 Getting chip information...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} chip-id"
        return self.run_command(cmd)
    
    def get_flash_id(self):
        """Get flash ID information"""
        print("💾 Getting flash ID...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} flash-id"
        return self.run_command(cmd)
    
    def read_flash(self, output_file, start=0x00000, size=0x100000, progress=True):
        """Read flash memory to binary file (1MB for ESP01)"""
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
        
        if file_size > 0x100000:  # 1MB limit for ESP01
            print("⚠️  Warning: File size exceeds ESP01 flash capacity (1MB)")
            return False
        
        print(f"📝 Writing firmware {firmware_file} to flash...")
        
        # Build command with options
        verify_flag = "--verify" if verify else ""
        progress_flag = "--progress" if progress else ""
        erase_flag = "--erase-all" if erase_all else ""
        
        cmd = f"esptool.py --port {self.port} --baud {self.baud} {progress_flag} write-flash --flash-mode {self.flash_mode} --flash-freq {self.flash_freq} --flash-size {self.flash_size} {verify_flag} {erase_flag} {address:08x} {firmware_file}"
        
        return self.run_command(cmd)
    
    def erase_flash(self):
        """Erase entire flash memory"""
        print("🗑️  Erasing flash memory...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} erase-flash"
        return self.run_command(cmd)
    
    def write_arduino_sketch(self, sketch_file, address=0x00000, verify=True):
        """Write Arduino sketch (compiled .bin file)"""
        return self.write_flash(sketch_file, address, verify)
    
    def backup_firmware(self, backup_file="esp01_backup.bin"):
        """Create a complete backup of current firmware"""
        print(f"💾 Creating firmware backup: {backup_file}")
        return self.read_flash(backup_file)
    
    def write_at_firmware(self, at_firmware_file, verify=True):
        """Write AT firmware to ESP01"""
        print("📡 Writing AT firmware to ESP01...")
        return self.write_flash(at_firmware_file, 0x00000, verify)
    
    def verify_flash(self, firmware_file, address=0x00000, size=0x100000):
        """Verify written firmware by reading it back and comparing"""
        print("🔍 Verifying written firmware...")
        
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
        """Get MAC address of the ESP01"""
        print("🔍 Getting MAC address...")
        cmd = f"esptool.py --port {self.port} --baud {self.baud} read-mac"
        return self.run_command(cmd)

def main():
    parser = argparse.ArgumentParser(
        description='ESP01 Flashing Tool - Enhanced with verification and progress tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get chip information
  python esp01_flash.py --port COM3 --action info
  
  # Backup current firmware
  python esp01_flash.py --port COM3 --action backup --file my_backup.bin
  
  # Write firmware with verification
  python esp01_flash.py --port COM3 --action write --file firmware.bin --verify
  
  # Write AT firmware
  python esp01_flash.py --port COM3 --action at_firmware --file at_firmware.bin
  
  # Erase flash memory
  python esp01_flash.py --port COM3 --action erase
        """
    )
    
    parser.add_argument('--port', required=True, help='Serial port (e.g., COM3, /dev/ttyUSB0)')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('--action', required=True, 
                       choices=['info', 'read', 'write', 'erase', 'backup', 'at_firmware', 'verify', 'mac', 'flash_id'], 
                       help='Action to perform')
    parser.add_argument('--file', help='File path for read/write operations')
    parser.add_argument('--address', default='0x00000', help='Memory address (hex, default: 0x00000)')
    parser.add_argument('--size', default='0x100000', help='Size to read (hex, default: 0x100000 for 1MB)')
    parser.add_argument('--verify', action='store_true', help='Verify written firmware (for write operations)')
    parser.add_argument('--no-progress', action='store_true', help='Disable progress bar')
    parser.add_argument('--erase-all', action='store_true', help='Erase entire flash before writing')
    parser.add_argument('--no-verify', action='store_true', help='Skip verification for write operations')
    
    args = parser.parse_args()
    
    # Convert hex strings to integers
    address = int(args.address, 16)
    size = int(args.size, 16)
    
    print("🚀 ESP01 Flashing Tool - Enhanced Version")
    print("=" * 50)
    
    flasher = ESP01Flasher(args.port, args.baud)
    
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
            print("📋 Getting ESP01 information...")
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
                
        elif args.action == 'erase':
            print("🗑️  Erasing flash memory...")
            success = flasher.erase_flash()
            if success:
                print("✓ Flash memory erased successfully!")
            else:
                print("❌ Failed to erase flash memory")
                sys.exit(1)
                
        elif args.action == 'backup':
            backup_file = args.file or "esp01_backup.bin"
            print(f"💾 Creating firmware backup: {backup_file}")
            success = flasher.backup_firmware(backup_file)
            if success:
                file_size = os.path.getsize(backup_file)
                print(f"✓ Backup created successfully: {file_size:,} bytes")
            else:
                print("❌ Failed to create backup")
                sys.exit(1)
                
        elif args.action == 'at_firmware':
            if not args.file:
                print("❌ Error: --file required for AT firmware operation")
                sys.exit(1)
            print(f"📡 Writing AT firmware: {args.file}")
            success = flasher.write_at_firmware(args.file, verify)
            if success:
                print("✓ AT firmware written successfully!")
            else:
                print("❌ Failed to write AT firmware")
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
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except (OSError, ValueError) as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    
    print("\n🎉 Operation completed successfully!")

if __name__ == "__main__":
    main()