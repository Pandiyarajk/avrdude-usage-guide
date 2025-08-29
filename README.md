# AVRDUDE Usage Guide (Windows x64)

This repository provides a simple guide and examples for installing and using **AVRDUDE v8.1** on Windows to read and write flash memory for Arduino boards (e.g., ATmega328P).

---

## 📥 Installation

1. Download the latest AVRDUDE release (Windows x64) from the official GitHub page:  
   👉 [avrdude-v8.1-windows-x64.zip](https://github.com/avrdudes/avrdude/releases)

2. Extract the contents of the ZIP file to:

   ```
   C:\avrdude
   ```

3. Ensure `avrdude.exe` is located at:

   ```
   C:\avrdude\avrdude.exe
   ```

---

## 🔍 Reading Flash Memory

You can dump (read) the contents of your Arduino’s flash memory into a file.

### Example: Read flash to HEX file
```bash
"C:\avrdude\avrdude.exe" -c arduino -P com8 -p atmega328p -U flash:r:d:\compiledcode.hex:i
```

- `-c arduino` → use Arduino bootloader protocol  
- `-P com8` → COM port of the Arduino (check Device Manager)  
- `-p atmega328p` → target microcontroller  
- `-U flash:r:d:\compiledcode.hex:i` → read flash, save as Intel HEX format  

### Example: Read flash to BIN file
```bash
"C:\avrdude\avrdude.exe" -c arduino -P com8 -p atmega328p -U flash:r:d:\compiledcode.bin:r
```

- `:r` at the end specifies **raw binary format** output.  

---

## ✍️ Writing Compiled Code (Flashing)

To upload a compiled `.hex` file to your Arduino:

```bash
"C:\avrdude\avrdude.exe" -c arduino -P com8 -p atmega328p -U flash:w:d:\compiledcode.hex:i
```

- `-U flash:w:...:i` → write the given HEX file in Intel format to flash memory.  

---

## ✅ Notes

- Make sure you are using the correct **COM port** (replace `com8` if needed).  
- Common baud rates: `115200` (new bootloaders) or `57600` (older boards/clones).  
- If upload fails with *“not in sync”* errors, try pressing **Reset** on the Arduino just before running the command.  
- For direct ISP programmers (e.g., USBasp), replace `-c arduino` with the appropriate programmer name.  

---

## 🚀 Quick Commands

- **Read flash to HEX**:  
  `avrdude -c arduino -P com8 -p atmega328p -U flash:r:compiledcode.hex:i`

- **Read flash to BIN**:  
  `avrdude -c arduino -P com8 -p atmega328p -U flash:r:compiledcode.bin:r`

- **Write HEX to Arduino**:  
  `avrdude -c arduino -P com8 -p atmega328p -U flash:w:compiledcode.hex:i`

- **Write BIN to Arduino**:  
  `avrdude -c arduino -P com8 -p atmega328p -U flash:w:compiledcode.bin:r`
---

## 📚 Reference

- [AVRDUDE GitHub Releases](https://github.com/avrdudes/avrdude/releases)  
- [Official AVRDUDE Documentation](https://avrdudes.github.io/avrdude/)
