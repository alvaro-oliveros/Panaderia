# ESP32 Bakery Sensor Setup Guide

## Hardware Wiring

### Components Required
- ESP32 DevKit
- DHT22 Temperature/Humidity Sensor
- 0.96" OLED Display (SSD1306)
- Active Buzzer
- 3x LEDs (Red, Yellow, Green)
- 3x 220Ω Resistors (for LEDs)
- Breadboard and jumper wires

### Pin Connections

| Component | ESP32 Pin | Notes |
|-----------|-----------|-------|
| DHT22 Data | GPIO 2 | Digital pin |
| DHT22 VCC | 3.3V | Power |
| DHT22 GND | GND | Ground |
| OLED SDA | GPIO 21 | I2C Data |
| OLED SCL | GPIO 22 | I2C Clock |
| OLED VCC | 3.3V | Power |
| OLED GND | GND | Ground |
| Buzzer + | GPIO 4 | Active buzzer |
| Buzzer - | GND | Ground |
| Green LED + | GPIO 5 | Through 220Ω resistor |
| Green LED - | GND | Ground |
| Yellow LED + | GPIO 18 | Through 220Ω resistor |
| Yellow LED - | GND | Ground |
| Red LED + | GPIO 19 | Through 220Ω resistor |
| Red LED - | GND | Ground |

## Software Setup

### 1. Arduino IDE Configuration
1. Install ESP32 board support in Arduino IDE
2. Install required libraries:
   - `DHT sensor library` by Adafruit
   - `Adafruit GFX Library`
   - `Adafruit SSD1306`
   - `ArduinoJson` by Benoit Blanchon

### 2. Code Configuration
Edit these settings in `esp32_bakery_sensor.ino`:

```cpp
// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";        // Replace with your WiFi name
const char* password = "YOUR_WIFI_PASSWORD"; // Replace with your WiFi password

// API Configuration  
const char* apiURL = "http://192.168.1.100:8000";  // Replace with your computer's IP
const int sensorID = 1;  // Replace with your sensor ID from database
```

### 3. Find Your Computer's IP Address
**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" under your WiFi adapter

**Mac/Linux:**
```bash
ifconfig
```
Look for "inet" address under your WiFi interface

**Example:** If your computer's IP is `192.168.1.150`, set:
```cpp
const char* apiURL = "http://192.168.1.150:8000";
```

### 4. Get Your Sensor ID
1. Start your bakery management system
2. Go to http://localhost:3000/login.html
3. Login as admin (username: `admin`, password: `admin123`)
4. Navigate to sensors section
5. Create a new sensor or note the ID of existing sensor
6. Update the `sensorID` variable in the code

## LED Status Indicators

| LED Color | Status | Meaning |
|-----------|---------|---------|
| Green | Solid | Optimal conditions (temp 16-25°C, humidity 45-65%) |
| Yellow | Solid | Warning conditions (temp 25-28°C, humidity 45-70%) |
| Red | Solid | Critical conditions (temp <16°C or >28°C, humidity <45% or >70%) |
| Red | Blinking | Sensor error or hardware failure |
| Yellow | Blinking | Connecting to WiFi |
| Green | Flash | WiFi connected successfully |

## Buzzer Alerts

- **3 beeps every 10 seconds:** Critical temperature or humidity conditions
- **Single beep:** WiFi connection successful
- **No sound:** Normal operation

## Alert Thresholds

Current thresholds (can be modified in code):
- **Temperature Critical:** < 16°C or > 28°C
- **Temperature Warning:** > 25°C  
- **Humidity Critical:** < 45% or > 70%
- **Humidity Warning:** < 50% or > 65%

## Troubleshooting

### WiFi Connection Issues
1. Verify SSID and password are correct
2. Check if ESP32 is within WiFi range
3. Ensure WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)
4. Monitor Serial output for connection attempts

### API Communication Issues
1. Verify your computer's IP address is correct
2. Ensure bakery management system is running
3. Check firewall settings on your computer
4. Test API endpoint: `curl http://YOUR_IP:8000/sensores/`

### Sensor Reading Issues
1. Check DHT22 wiring connections
2. Verify power supply (3.3V)
3. Allow 2-3 minutes for sensor to stabilize after power-on
4. Monitor Serial output for sensor errors

### Display Issues
1. Check I2C connections (SDA/SCL)
2. Verify OLED address is 0x3C
3. Check power supply to OLED

## Data Integration

The sensor automatically sends data to your bakery management system every 15 seconds:
- Temperature data goes to `/temperatura/` endpoint
- Humidity data goes to `/humedad/` endpoint
- Data can be viewed at http://localhost:3000/temperatura.html and http://localhost:3000/humedad.html

## Optimal Bakery Conditions

For reference, ideal bakery storage conditions:
- **Temperature:** 18-24°C (64-75°F)
- **Humidity:** 50-60% RH
- **Bread Storage:** 55-65% RH
- **Pastry Storage:** 45-55% RH

The sensor will alert you when conditions move outside these optimal ranges to help maintain product quality.