# ESP Board Flashing Tools

This repository provides comprehensive tools and guides for flashing ESP8266 NodeMCU, ESP01, and ESP32 boards using **esptool.py** - the official tool for ESP chip programming.

## 🚀 Quick Start

### 1. Installation
```bash
# Install esptool.py
pip install esptool

# Or run the automated installer
python install_esptool.py
```

### 2. Basic Usage

**ESP8266 NodeMCU:**
```bash
python esp8266_flash.py --port COM3 --action info
python esp8266_flash.py --port COM3 --action backup
python esp8266_flash.py --port COM3 --action write --file firmware.bin
```

**ESP01:**
```bash
python esp01_flash.py --port COM3 --action info
python esp01_flash.py --port COM3 --action backup
python esp01_flash.py --port COM3 --action write --file firmware.bin
```

**ESP32:**
```bash
python esp32_flash.py --port COM3 --action info
python esp32_flash.py --port COM3 --action backup
python esp32_flash.py --port COM3 --action write_complete --bootloader bootloader.bin --partition_table partition-table.bin --app app.bin
```

## 📁 Files Overview

| File | Description |
|------|-------------|
| `ESP_Flashing_Guide.md` | Comprehensive guide for all ESP boards |
| `esp8266_flash.py` | Automated script for ESP8266 NodeMCU |
| `esp01_flash.py` | Automated script for ESP01 (1MB flash) |
| `esp32_flash.py` | Automated script for ESP32 |
| `install_esptool.py` | Automated installation script |
| `README_ESP.md` | This file |

## 🔧 Features

### ESP8266 NodeMCU Support
- ✅ Read/write flash memory
- ✅ Backup firmware
- ✅ Erase flash
- ✅ Arduino sketch flashing
- ✅ Chip information

### ESP01 Support
- ✅ Read/write flash memory (1MB)
- ✅ Backup firmware
- ✅ Erase flash
- ✅ AT firmware support
- ✅ Arduino sketch flashing

### ESP32 Support
- ✅ Read/write flash memory
- ✅ Complete firmware flashing (bootloader + partition table + app)
- ✅ Individual partition reading
- ✅ Backup firmware
- ✅ Erase flash
- ✅ Arduino sketch flashing

## 🛠️ Common Operations

### Backup Current Firmware
```bash
# ESP8266
python esp8266_flash.py --port COM3 --action backup --file my_backup.bin

# ESP01
python esp01_flash.py --port COM3 --action backup --file esp01_backup.bin

# ESP32
python esp32_flash.py --port COM3 --action backup --file esp32_backup.bin
```

### Flash New Firmware
```bash
# ESP8266/ESP01 - Single binary
python esp8266_flash.py --port COM3 --action write --file new_firmware.bin

# ESP32 - Complete firmware
python esp32_flash.py --port COM3 --action write_complete \
  --bootloader bootloader.bin \
  --partition_table partition-table.bin \
  --app app.bin
```

### Read Specific Partitions (ESP32)
```bash
# Read bootloader
python esp32_flash.py --port COM3 --action read_partition --partition bootloader --file bootloader.bin

# Read application
python esp32_flash.py --port COM3 --action read_partition --partition app --file app.bin
```

## 🔍 Troubleshooting

### Common Issues

1. **"Failed to connect"**
   - Check COM port (Device Manager on Windows)
   - Try different baud rates
   - Hold BOOT button while connecting

2. **"Permission denied" (Linux/Mac)**
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   sudo usermod -a -G dialout $USER
   ```

3. **"Not in sync"**
   - Press RESET while holding BOOT
   - Try different baud rates

### Entering Download Mode

**ESP8266/ESP01:**
1. Hold GPIO0 to GND
2. Press and release RESET
3. Release GPIO0

**ESP32:**
1. Hold BOOT button
2. Press and release EN (Reset)
3. Release BOOT button

## 📚 Documentation

- [ESP_Flashing_Guide.md](ESP_Flashing_Guide.md) - Complete reference guide
- [esptool.py Documentation](https://github.com/espressif/esptool)
- [ESP8266 Arduino Core](https://github.com/esp8266/Arduino)
- [ESP32 Arduino Core](https://github.com/espressif/arduino-esp32)

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).