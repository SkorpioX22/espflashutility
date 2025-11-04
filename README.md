# espflashutility
Tool for onboard USB UART flashing of Espressif chipsets such as the ESP32, ESP8266, and their variants. Flashing is done via esptool.

## Requirements

- **Python 3.10+**
- **pip** package manager
- **latest version of ESPtool: https://docs.espressif.com/projects/esptool/en/latest/esp32/installation.html**
Install the required Python packages:

```bash
pip install esptool pyserial tk
```

## Supported Chips and Modules

### ESP32 Family Variants

| Chip / Module Name      | Identifier  | Notes |
|-------------------------|------------|------|
| ESP32                   | `esp32`     | Standard dual-core Xtensa LX6 |
| ESP32-S2                | `esp32s2`   | Single-core, native USB, improved security |
| ESP32-S3                | `esp32s3`   | Dual-core, AI acceleration, vector instructions |
| ESP32-C2                | `esp32c2`   | Single-core RISC-V, BLE + Wi-Fi |
| ESP32-C3                | `esp32c3`   | Single-core RISC-V, BLE + Wi-Fi, secure boot |
| ESP32-C6                | `esp32c6`   | Single-core RISC-V, Wi-Fi 6 + BLE |
| ESP32-H2                | `esp32h2`   | Single-core RISC-V, BLE + IEEE 802.15.4 |
| ESP32-P4                | `esp32p4`   | High-performance variant for AI/control |

**Popular Modules (ESP32 variants packaged for boards)**

| Module Name             | Base Chip  | Notes |
|-------------------------|-----------|------|
| ESP32-WROOM-32           | ESP32     | Most common dev module, 4MB Flash |
| ESP32-WROOM-32D          | ESP32     | Improved thermal performance |
| ESP32-WROOM-32U          | ESP32     | U.FL connector for external antenna |
| ESP32-WROOM-32E          | ESP32     | Enhanced WROOM variant |
| ESP32-WROVER             | ESP32     | Includes PSRAM for more memory |
| ESP32-WROVER-B           | ESP32     | PSRAM + 4MB Flash |
| ESP32-WROVER-IE          | ESP32     | Industrial temp range |
| ESP32-DA / ESP32-DA2     | ESP32     | Dual antenna / improved RF |
| ESP32-S2-WROOM            | ESP32-S2 | Standard S2 module |
| ESP32-S2-WROVER           | ESP32-S2 | S2 module with PSRAM |
| ESP32-S3-WROOM            | ESP32-S3 | Standard S3 module |
| ESP32-S3-WROVER           | ESP32-S3 | S3 module with PSRAM |
| ESP32-C3-WROOM            | ESP32-C3 | Standard C3 module |
| ESP32-C6-WROOM            | ESP32-C6 | Standard C6 module |
| ESP32-H2-WROOM            | ESP32-H2 | Standard H2 module |

### ESP8266 Family Variants

| Chip / Module Name | Identifier  | Notes |
|-------------------|------------|------|
| ESP8266           | `esp8266`  | Classic single-core Wi-Fi module |
| ESP-01            | ESP8266    | Small 2x4 pin module |
| ESP-12 / ESP-12E  | ESP8266    | Most common dev module with GPIOs |
| ESP-12F / ESP-12S  | ESP8266   | Improved PCB antenna and performance |
