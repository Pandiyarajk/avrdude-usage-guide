# ESP Board Flashing Guide (ESP8266, ESP01, ESP32)

This repository provides a comprehensive guide for flashing ESP8266 NodeMCU, ESP01, and ESP32 boards using **esptool.py** - the official tool for ESP chip programming.

---

## 📥 Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package manager)

### Install esptool.py
```bash
pip install esptool
```

### Verify Installation
```bash
esptool.py version
```

---

## 🔍 Reading Flash Memory

### ESP8266 NodeMCU
```bash
# Read entire flash (4MB) to binary file
esptool.py --port COM3 --baud 115200 read_flash 0x00000 0x400000 esp8266_backup.bin

# Read specific size (1MB)
esptool.py --port COM3 --baud 115200 read_flash 0x00000 0x100000 esp8266_1mb.bin
```

### ESP01 (1MB Flash)
```bash
# Read entire flash (1MB) to binary file
esptool.py --port COM3 --baud 115200 read_flash 0x00000 0x100000 esp01_backup.bin
```

### ESP32
```bash
# Read entire flash (4MB) to binary file
esptool.py --port COM3 --baud 115200 read_flash 0x00000 0x400000 esp32_backup.bin

# Read specific partitions
esptool.py --port COM3 --baud 115200 read_flash 0x1000 0x6000 bootloader.bin
esptool.py --port COM3 --baud 115200 read_flash 0x10000 0x100000 app.bin
```

---

## ✍️ Writing Compiled Code (Flashing)

### ESP8266 NodeMCU
```bash
# Flash firmware binary
esptool.py --port COM3 --baud 115200 write_flash 0x00000 firmware.bin

# Flash with specific memory map
esptool.py --port COM3 --baud 115200 write_flash \
  --flash_mode dio \
  --flash_freq 40m \
  --flash_size 4MB \
  0x00000 boot_v1.7.bin \
  0x1000 user1.bin \
  0x3FC000 esp_init_data_default.bin
```

### ESP01 (1MB Flash)
```bash
# Flash firmware (ESP01 typically has 1MB flash)
esptool.py --port COM3 --baud 115200 write_flash \
  --flash_mode dio \
  --flash_freq 40m \
  --flash_size 1MB \
  0x00000 firmware.bin
```

### ESP32
```bash
# Flash complete firmware
esptool.py --port COM3 --baud 115200 write_flash \
  --flash_mode dio \
  --flash_freq 40m \
  --flash_size 4MB \
  0x1000 bootloader.bin \
  0x8000 partition-table.bin \
  0x10000 app.bin

# Flash single binary
esptool.py --port COM3 --baud 115200 write_flash 0x10000 app.bin
```

---

## 🔧 Board-Specific Commands

### ESP8266 NodeMCU Quick Commands
```bash
# Read flash to BIN
esptool.py --port COM3 --baud 115200 read_flash 0x00000 0x400000 esp8266_backup.bin

# Write firmware
esptool.py --port COM3 --baud 115200 write_flash 0x00000 firmware.bin

# Erase flash
esptool.py --port COM3 --baud 115200 erase_flash

# Chip info
esptool.py --port COM3 --baud 115200 chip_id
```

### ESP01 Quick Commands
```bash
# Read flash to BIN (1MB)
esptool.py --port COM3 --baud 115200 read_flash 0x00000 0x100000 esp01_backup.bin

# Write firmware
esptool.py --port COM3 --baud 115200 write_flash 0x00000 firmware.bin

# Erase flash
esptool.py --port COM3 --baud 115200 erase_flash
```

### ESP32 Quick Commands
```bash
# Read flash to BIN
esptool.py --port COM3 --baud 115200 read_flash 0x00000 0x400000 esp32_backup.bin

# Write complete firmware
esptool.py --port COM3 --baud 115200 write_flash 0x1000 bootloader.bin 0x8000 partition-table.bin 0x10000 app.bin

# Erase flash
esptool.py --port COM3 --baud 115200 erase_flash

# Chip info
esptool.py --port COM3 --baud 115200 chip_id
```

---

## 🚨 Troubleshooting

### Common Issues

1. **"Failed to connect" errors**
   - Check COM port (use Device Manager on Windows)
   - Try different baud rates (115200, 460800, 921600)
   - Hold BOOT button while connecting

2. **"Not in sync" errors**
   - Press and hold RESET button
   - Release RESET while holding BOOT
   - Release BOOT after connection established

3. **"Permission denied" (Linux/Mac)**
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   # or add user to dialout group
   sudo usermod -a -G dialout $USER
   ```

4. **Flash size errors**
   - Verify correct flash size parameter
   - ESP01: 1MB, ESP8266: 4MB, ESP32: 4MB (default)

### Entering Download Mode

**ESP8266/ESP01:**
1. Hold GPIO0 (D3) to GND
2. Press and release RESET
3. Release GPIO0

**ESP32:**
1. Hold BOOT button
2. Press and release EN (Reset)
3. Release BOOT button

---

## 📚 Reference

- [esptool.py GitHub](https://github.com/espressif/esptool)
- [ESP8266 Arduino Core](https://github.com/esp8266/Arduino)
- [ESP32 Arduino Core](https://github.com/espressif/arduino-esp32)
- [ESP32 Technical Reference Manual](https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf)

---

## 🔄 Port Detection

### Windows
```bash
# List available COM ports
mode
# or check Device Manager
```

### Linux/Mac
```bash
# List available serial ports
ls /dev/tty*
# Common ESP ports: /dev/ttyUSB0, /dev/ttyACM0
```

### Auto-detect ESP chip
```bash
esptool.py --port COM3 chip_id
```