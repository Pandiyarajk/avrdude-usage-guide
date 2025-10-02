#!/usr/bin/env python3
"""
Installation script for esptool.py and ESP development tools
Supports Windows, Linux, and macOS
"""

import subprocess
import sys
import platform
import os
from pathlib import Path

def run_command(cmd, check=True):
    """Run command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        print(f"✓ {cmd}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running: {cmd}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ Python 3.6 or higher is required!")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_esptool():
    """Install esptool.py"""
    print("\n📦 Installing esptool.py...")
    
    # Try pip3 first, then pip
    for pip_cmd in ['pip3', 'pip']:
        if run_command(f"{pip_cmd} --version", check=False):
            if run_command(f"{pip_cmd} install esptool"):
                return True
    
    print("❌ Failed to install esptool.py")
    return False

def install_arduino_cores():
    """Install Arduino cores for ESP boards"""
    print("\n📦 Installing Arduino ESP cores...")
    
    # Check if Arduino CLI is installed
    if not run_command("arduino-cli version", check=False):
        print("⚠️  Arduino CLI not found. Installing Arduino CLI...")
        install_arduino_cli()
    
    # Install ESP32 core
    print("Installing ESP32 Arduino core...")
    run_command("arduino-cli core install esp32:esp32")
    
    # Install ESP8266 core
    print("Installing ESP8266 Arduino core...")
    run_command("arduino-cli core install esp8266:esp8266")
    
    return True

def install_arduino_cli():
    """Install Arduino CLI"""
    system = platform.system().lower()
    
    if system == "windows":
        print("Installing Arduino CLI on Windows...")
        # Download and install Arduino CLI
        run_command("powershell -Command \"iwr -useb https://raw.githubusercontent.com/arduino/arduino-cli/master/install.ps1 | iex\"")
    elif system == "linux":
        print("Installing Arduino CLI on Linux...")
        run_command("curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh")
        # Add to PATH
        home = Path.home()
        arduino_cli_path = home / "bin" / "arduino-cli"
        if arduino_cli_path.exists():
            print(f"Add {arduino_cli_path.parent} to your PATH")
    elif system == "darwin":
        print("Installing Arduino CLI on macOS...")
        run_command("brew install arduino-cli")
    else:
        print(f"❌ Unsupported system: {system}")
        return False
    
    return True

def install_drivers():
    """Install USB-to-Serial drivers if needed"""
    system = platform.system().lower()
    
    if system == "windows":
        print("\n🔌 USB-to-Serial Driver Installation (Windows)")
        print("For ESP boards, you may need to install CH340 or CP2102 drivers:")
        print("• CH340 driver: https://www.wch.cn/downloads/CH341SER_ZIP.html")
        print("• CP2102 driver: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers")
        print("• FTDI driver: https://ftdichip.com/drivers/vcp-drivers/")
    elif system == "linux":
        print("\n🔌 Linux USB-to-Serial Setup")
        print("Add your user to the dialout group:")
        print("sudo usermod -a -G dialout $USER")
        print("Then log out and log back in.")
    elif system == "darwin":
        print("\n🔌 macOS USB-to-Serial Setup")
        print("macOS should automatically recognize most USB-to-Serial adapters.")
        print("If you have issues, try installing FTDI VCP drivers.")

def verify_installation():
    """Verify that esptool.py is installed correctly"""
    print("\n🔍 Verifying installation...")

    if run_command("python -m esptool version"):
        print("✓ esptool.py installed successfully!")
        return True
    else:
        print("❌ esptool.py verification failed")
        return False

def create_example_scripts():
    """Create example usage scripts"""
    print("\n📝 Creating example scripts...")
    
    # Make scripts executable on Unix systems
    if platform.system().lower() != "windows":
        for script in ["esp8266_flash.py", "esp01_flash.py", "esp32_flash.py"]:
            if os.path.exists(script):
                os.chmod(script, 0o755)
                print(f"✓ Made {script} executable")

def main():
    print("🚀 ESP Board Development Environment Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install esptool.py
    if not install_esptool():
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        sys.exit(1)
    
    # Install Arduino cores (optional)
    install_arduino_cores()
    
    # Install drivers info
    install_drivers()
    
    # Create example scripts
    create_example_scripts()
    
    print("\n🎉 Installation complete!")
    print("\nNext steps:")
    print("1. Connect your ESP board to your computer")
    print("2. Find the COM port (Windows) or device path (Linux/Mac)")
    print("3. Use esptool to interact with your board:")
    print("   • python -m esptool --port COM3 chip_id")
    print("   • python -m esptool --port COM3 flash_id")
    print("   • python -m esptool --port COM3 erase_flash")
    print("\nFor detailed usage, see ESP_Flashing_Guide.md")

if __name__ == "__main__":
    main()
