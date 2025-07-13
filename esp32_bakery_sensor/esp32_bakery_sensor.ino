#include "DHT.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include <EEPROM.h>
#include <WebServer.h>
#include <DNSServer.h>

// --- Hardware Configuration ---
#define DHTPIN 2        // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22   // DHT22 sensor type

#define SCREEN_WIDTH 128 // OLED width in pixels
#define SCREEN_HEIGHT 64 // OLED height in pixels
#define OLED_ADDR 0x3C   // OLED I2C address

// New hardware pins
#define BUZZER_PIN 4     // Active buzzer pin
#define LED_GREEN 5      // Green LED - Good conditions
#define LED_YELLOW 18    // Yellow LED - Warning conditions  
#define LED_RED 19       // Red LED - Critical conditions
#define CONFIG_BUTTON 0  // Configuration mode button (BOOT button)

// --- Configuration Structure ---
struct Config {
  char ssid[64];
  char password[64];
  char apiURL[128];
  int sensorID;
  bool configured;
  char checksum[16]; // Simple validation
};

// --- Default Configuration (fallback) ---
const char* DEFAULT_SSID = "AlvaroPhone";
const char* DEFAULT_PASSWORD = "Alvarooo";
const char* DEFAULT_API_URL = "http://3.12.34.248:8000";
const int DEFAULT_SENSOR_ID = 1;

// --- Configuration Variables ---
Config deviceConfig;
bool configMode = false;

// --- Configuration Portal ---
WebServer configServer(80);
DNSServer dnsServer;
const char* AP_NAME = "BakerySensor-Config";

// EEPROM Configuration
#define EEPROM_SIZE 512
#define CONFIG_START_ADDRESS 0

// --- Timezone Configuration ---
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = -5 * 3600;  // Lima, Peru is UTC-5
const int daylightOffset_sec = 0;      // Peru doesn't use daylight saving time

// --- Alert Thresholds (Adjusted for Lima's humid climate) ---
const float TEMP_CRITICAL_HIGH = 28.0;   // °C
const float TEMP_CRITICAL_LOW = 16.0;    // °C
const float HUMIDITY_CRITICAL_HIGH = 75.0; // % (Raised for Lima's humidity)
const float HUMIDITY_CRITICAL_LOW = 45.0;  // %

// --- Create Objects ---
DHT dht(DHTPIN, DHTTYPE);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// --- Global Variables ---
bool wifiConnected = false;
unsigned long lastSensorRead = 0;
unsigned long lastAPICall = 0;

// === Configuration Functions ===

void saveConfigToEEPROM() {
  EEPROM.begin(EEPROM_SIZE);
  strcpy(deviceConfig.checksum, "BAKERY_V1");
  deviceConfig.configured = true;
  
  EEPROM.put(CONFIG_START_ADDRESS, deviceConfig);
  EEPROM.commit();
  EEPROM.end();
  
  Serial.println("Configuration saved to EEPROM");
}

bool loadConfigFromEEPROM() {
  EEPROM.begin(EEPROM_SIZE);
  EEPROM.get(CONFIG_START_ADDRESS, deviceConfig);
  EEPROM.end();
  
  // Validate checksum
  if (strcmp(deviceConfig.checksum, "BAKERY_V1") == 0 && deviceConfig.configured) {
    Serial.println("Valid configuration loaded from EEPROM");
    return true;
  } else {
    Serial.println("No valid configuration found, using defaults");
    setDefaultConfig();
    return false;
  }
}

void setDefaultConfig() {
  strcpy(deviceConfig.ssid, DEFAULT_SSID);
  strcpy(deviceConfig.password, DEFAULT_PASSWORD);
  strcpy(deviceConfig.apiURL, DEFAULT_API_URL);
  deviceConfig.sensorID = DEFAULT_SENSOR_ID;
  deviceConfig.configured = false;
  strcpy(deviceConfig.checksum, "BAKERY_V1");
}

bool isConfigButtonPressed() {
  return digitalRead(CONFIG_BUTTON) == LOW;
}

// === Configuration Web Server ===

void setupConfigServer() {
  // Set up Access Point
  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_NAME);
  
  // Set up DNS server to redirect all requests to configuration page
  dnsServer.start(53, "*", WiFi.softAPIP());
  
  // Configuration page
  configServer.on("/", handleConfigPage);
  configServer.on("/save", handleConfigSave);
  configServer.on("/status", handleConfigStatus);
  configServer.onNotFound(handleConfigPage); // Redirect all requests to config page
  
  configServer.begin();
  
  Serial.println("Configuration server started");
  Serial.print("Connect to WiFi: ");
  Serial.println(AP_NAME);
  Serial.print("Open browser to: http://");
  Serial.println(WiFi.softAPIP());
}

void handleConfigPage() {
  String html = "<!DOCTYPE html><html><head>";
  html += "<title>Bakery Sensor Configuration</title>";
  html += "<meta name='viewport' content='width=device-width,initial-scale=1'>";
  html += "<style>body{font-family:Arial;margin:20px;background:#f0f0f0}";
  html += ".container{background:white;padding:20px;border-radius:10px;max-width:400px;margin:0 auto}";
  html += "h1{color:#333;text-align:center}input{width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:5px}";
  html += "button{width:100%;padding:15px;background:#007bff;color:white;border:none;border-radius:5px;font-size:16px;cursor:pointer}";
  html += "button:hover{background:#0056b3}.info{background:#e7f3ff;padding:10px;border-radius:5px;margin:10px 0}</style>";
  html += "</head><body><div class='container'>";
  html += "<h1>🍞 Bakery Sensor Config</h1>";
  
  html += "<div class='info'>Current Settings:<br>";
  html += "WiFi: " + String(deviceConfig.ssid) + "<br>";
  html += "API: " + String(deviceConfig.apiURL) + "<br>";
  html += "Sensor ID: " + String(deviceConfig.sensorID) + "</div>";
  
  html += "<form action='/save' method='POST'>";
  html += "<label>WiFi Network:</label>";
  html += "<input type='text' name='ssid' value='" + String(deviceConfig.ssid) + "' required>";
  html += "<label>WiFi Password:</label>";
  html += "<input type='password' name='password' value='" + String(deviceConfig.password) + "' required>";
  html += "<label>API URL:</label>";
  html += "<input type='text' name='apiURL' value='" + String(deviceConfig.apiURL) + "' required>";
  html += "<label>Sensor ID:</label>";
  html += "<input type='number' name='sensorID' value='" + String(deviceConfig.sensorID) + "' required>";
  html += "<button type='submit'>Save Configuration</button>";
  html += "</form>";
  html += "<p style='text-align:center;color:#666;font-size:12px'>After saving, the sensor will restart and connect to your WiFi.</p>";
  html += "</div></body></html>";
  
  configServer.send(200, "text/html", html);
}

void handleConfigSave() {
  // Get form data
  if (configServer.hasArg("ssid") && configServer.hasArg("password") && 
      configServer.hasArg("apiURL") && configServer.hasArg("sensorID")) {
    
    strcpy(deviceConfig.ssid, configServer.arg("ssid").c_str());
    strcpy(deviceConfig.password, configServer.arg("password").c_str());
    strcpy(deviceConfig.apiURL, configServer.arg("apiURL").c_str());
    deviceConfig.sensorID = configServer.arg("sensorID").toInt();
    
    // Save to EEPROM
    saveConfigToEEPROM();
    
    String html = "<!DOCTYPE html><html><head>";
    html += "<title>Configuration Saved</title>";
    html += "<meta name='viewport' content='width=device-width,initial-scale=1'>";
    html += "<style>body{font-family:Arial;margin:20px;background:#f0f0f0;text-align:center}";
    html += ".container{background:white;padding:20px;border-radius:10px;max-width:400px;margin:0 auto}";
    html += "h1{color:#28a745}</style>";
    html += "</head><body><div class='container'>";
    html += "<h1>✅ Configuration Saved!</h1>";
    html += "<p>The sensor will restart in 5 seconds and connect to your WiFi network.</p>";
    html += "<p><strong>WiFi:</strong> " + String(deviceConfig.ssid) + "</p>";
    html += "<p><strong>API:</strong> " + String(deviceConfig.apiURL) + "</p>";
    html += "</div></body></html>";
    
    configServer.send(200, "text/html", html);
    
    Serial.println("Configuration saved, restarting in 5 seconds...");
    delay(5000);
    ESP.restart();
  } else {
    configServer.send(400, "text/plain", "Missing required parameters");
  }
}

void handleConfigStatus() {
  String json = "{";
  json += "\"ssid\":\"" + String(deviceConfig.ssid) + "\",";
  json += "\"apiURL\":\"" + String(deviceConfig.apiURL) + "\",";
  json += "\"sensorID\":" + String(deviceConfig.sensorID) + ",";
  json += "\"configured\":" + String(deviceConfig.configured ? "true" : "false");
  json += "}";
  configServer.send(200, "application/json", json);
}
const unsigned long SENSOR_INTERVAL = 2000;  // Read sensor every 2 seconds
const unsigned long API_INTERVAL = 15000;    // Send to API every 15 seconds
const unsigned long SENSOR_WARMUP_TIME = 30000;  // DHT22 warm-up time (30 seconds)

float currentTemp = 0.0;
float currentHumidity = 0.0;
bool sensorError = false;
bool sensorWarmedUp = false;
unsigned long sensorStartTime = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 Bakery Sensor System Starting...");

  // Initialize hardware
  initializePins();
  initializeDisplay();
  initializeSensor();
  
  // Load configuration from EEPROM
  loadConfigFromEEPROM();
  
  // Check if configuration button is pressed during startup
  if (isConfigButtonPressed()) {
    Serial.println("Configuration button pressed - entering configuration mode");
    configMode = true;
    
    // Display configuration mode on OLED
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.println("CONFIG MODE");
    display.println("Connect to WiFi:");
    display.println(AP_NAME);
    display.println("Open browser to:");
    display.println("192.168.4.1");
    display.display();
    
    // Start configuration server
    setupConfigServer();
    
    // Stay in configuration mode
    while (configMode) {
      dnsServer.processNextRequest();
      configServer.handleClient();
      delay(10);
    }
  } else {
    // Normal operation mode
    connectToWiFi();
    
    // Initialize time synchronization
    if (wifiConnected) {
      initializeTime();
    }
    
    Serial.println("System initialized successfully!");
  }
}

void loop() {
  // Read sensor data
  if (millis() - lastSensorRead >= SENSOR_INTERVAL) {
    readSensorData();
    updateDisplay();
    updateAlerts();
    lastSensorRead = millis();
  }
  
  // Send data to API (only after warm-up is complete)
  if (millis() - lastAPICall >= API_INTERVAL && wifiConnected && !sensorError && sensorWarmedUp) {
    sendDataToAPI();
    lastAPICall = millis();
  }
  
  // Check WiFi connection
  if (!WiFi.isConnected() && wifiConnected) {
    wifiConnected = false;
    Serial.println("WiFi connection lost. Attempting to reconnect...");
    connectToWiFi();
  }
  
  delay(100);
}

void initializePins() {
  // Initialize LEDs
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  
  // Initialize buzzer
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Initialize configuration button with pullup
  pinMode(CONFIG_BUTTON, INPUT_PULLUP);
  
  // Test all outputs
  testOutputs();
}

void initializeDisplay() {
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;); // halt if display not found
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Bakery Sensor v2.0");
  display.println("Initializing...");
  display.display();
  delay(2000);
}

void initializeSensor() {
  dht.begin();
  sensorStartTime = millis();  // Record start time for warm-up period
  
  Serial.println("DHT22 sensor initialized - warming up for 30 seconds...");
  Serial.println("Please wait for accurate readings...");
}

void initializeTime() {
  Serial.println("Initializing time synchronization...");
  
  // Configure time with NTP server for Lima, Peru (UTC-5)
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  
  // Wait for time to be synchronized
  int retries = 0;
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo) && retries < 10) {
    delay(1000);
    retries++;
    Serial.print(".");
  }
  
  if (retries >= 10) {
    Serial.println("Failed to obtain time from NTP server");
    return;
  }
  
  Serial.println();
  Serial.println("Time synchronized successfully!");
  Serial.print("Current Lima time: ");
  Serial.println(&timeinfo, "%A, %B %d %Y %H:%M:%S");
  
  // Print UTC time for comparison
  time_t now = time(nullptr);
  struct tm* utc_tm = gmtime(&now);
  Serial.print("UTC time: ");
  Serial.println(utc_tm, "%A, %B %d %Y %H:%M:%S");
}

String getCurrentTimestamp() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    return "";
  }
  
  // Debug: Print what time we're getting
  Serial.print("Local time for timestamp: ");
  Serial.println(&timeinfo, "%Y-%m-%d %H:%M:%S");
  
  char timestamp[25];
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S", &timeinfo);
  return String(timestamp);
}

void connectToWiFi() {
  setLEDStatus("connecting");
  
  Serial.print("Connecting to WiFi network: ");
  Serial.println(deviceConfig.ssid);
  
  // Try to improve compatibility
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  
  WiFi.begin(deviceConfig.ssid, deviceConfig.password);
  Serial.print("Connecting to WiFi");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
    
    // Print WiFi status every 5 attempts
    if (attempts % 5 == 0) {
      Serial.print(" [Status: ");
      Serial.print(WiFi.status());
      Serial.print("]");
    }
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println();
    Serial.print("WiFi connected! IP: ");
    Serial.println(WiFi.localIP());
    
    // Success beep
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
    
    setLEDStatus("connected");
  } else {
    wifiConnected = false;
    Serial.println();
    Serial.println("WiFi connection failed!");
    setLEDStatus("error");
  }
}

void readSensorData() {
  // Check if sensor warm-up period is complete
  if (!sensorWarmedUp) {
    if (millis() - sensorStartTime >= SENSOR_WARMUP_TIME) {
      sensorWarmedUp = true;
      Serial.println("DHT22 warm-up complete - readings are now accurate!");
    } else {
      // Still warming up - show countdown
      unsigned long remaining = (SENSOR_WARMUP_TIME - (millis() - sensorStartTime)) / 1000;
      Serial.printf("Warming up... %lu seconds remaining\n", remaining);
      return;  // Don't read sensor yet
    }
  }
  
  currentHumidity = dht.readHumidity();
  currentTemp = dht.readTemperature(false);
  
  if (isnan(currentHumidity) || isnan(currentTemp)) {
    Serial.println("Failed to read from DHT sensor!");
    sensorError = true;
  } else {
    sensorError = false;
    Serial.printf("Temp: %.1f°C, Humidity: %.1f%%\n", currentTemp, currentHumidity);
  }
}

void updateDisplay() {
  display.clearDisplay();
  
  // Title
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("Panaderia");
  
  // WiFi Status
  display.setCursor(70, 0);
  if (wifiConnected) {
    display.print("WiFi:OK");
  } else {
    display.print("WiFi:--");
  }
  
  if (sensorError) {
    display.setTextSize(1);
    display.setCursor(0, 20);
    display.println("SENSOR ERROR!");
    display.setCursor(0, 35);
    display.println("Check connections");
  } else if (!sensorWarmedUp) {
    // Show warm-up countdown
    display.setTextSize(1);
    display.setCursor(0, 20);
    display.println("WARMING UP...");
    display.setCursor(0, 35);
    unsigned long remaining = (SENSOR_WARMUP_TIME - (millis() - sensorStartTime)) / 1000;
    display.print("Wait: ");
    display.print(remaining);
    display.println("s");
  } else {
    // Temperature (large)
    display.setTextSize(2);
    display.setCursor(0, 15);
    display.print(currentTemp, 1);
    display.print((char)247); // Degree symbol
    display.println("C");
    
    // Humidity
    display.setTextSize(1);
    display.setCursor(0, 40);
    display.print("Humedad: ");
    display.print(currentHumidity, 1);
    display.println("%");
    
    // Status
    display.setCursor(0, 55);
    String status = getEnvironmentStatus();
    display.print(status);
  }
  
  display.display();
}

void updateAlerts() {
  if (sensorError) {
    setLEDStatus("error");
    return;
  }
  
  bool tempCritical = (currentTemp > TEMP_CRITICAL_HIGH || currentTemp < TEMP_CRITICAL_LOW);
  bool humidityCritical = (currentHumidity > HUMIDITY_CRITICAL_HIGH || currentHumidity < HUMIDITY_CRITICAL_LOW);
  
  if (tempCritical || humidityCritical) {
    setLEDStatus("critical");
    soundAlert();
  } else if (currentTemp > 25.0 || (currentHumidity >= 70.0 && currentHumidity <= 75.0) || (currentHumidity >= 45.0 && currentHumidity < 50.0)) {
    setLEDStatus("warning");
  } else {
    setLEDStatus("good");
  }
}

void setLEDStatus(String status) {
  // Turn off all LEDs first
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
  
  if (status == "good") {
    digitalWrite(LED_GREEN, HIGH);
  } else if (status == "warning") {
    digitalWrite(LED_YELLOW, HIGH);
  } else if (status == "critical") {
    digitalWrite(LED_RED, HIGH);
  } else if (status == "error") {
    // Blink red for error
    static unsigned long lastBlink = 0;
    static bool blinkState = false;
    if (millis() - lastBlink > 500) {
      blinkState = !blinkState;
      digitalWrite(LED_RED, blinkState);
      lastBlink = millis();
    }
  } else if (status == "connecting") {
    // Blink yellow for connecting
    static unsigned long lastBlink = 0;
    static bool blinkState = false;
    if (millis() - lastBlink > 300) {
      blinkState = !blinkState;
      digitalWrite(LED_YELLOW, blinkState);
      lastBlink = millis();
    }
  } else if (status == "connected") {
    // Brief green flash
    digitalWrite(LED_GREEN, HIGH);
    delay(100);
    digitalWrite(LED_GREEN, LOW);
  }
}

void soundAlert() {
  static unsigned long lastAlert = 0;
  
  // Sound alert every 10 seconds for critical conditions
  if (millis() - lastAlert > 10000) {
    for (int i = 0; i < 3; i++) {
      digitalWrite(BUZZER_PIN, HIGH);
      delay(200);
      digitalWrite(BUZZER_PIN, LOW);
      delay(200);
    }
    lastAlert = millis();
  }
}

String getEnvironmentStatus() {
  if (sensorError) {
    return "ERROR";
  }
  
  bool tempCritical = (currentTemp > TEMP_CRITICAL_HIGH || currentTemp < TEMP_CRITICAL_LOW);
  bool humidityCritical = (currentHumidity > HUMIDITY_CRITICAL_HIGH || currentHumidity < HUMIDITY_CRITICAL_LOW);
  
  if (tempCritical || humidityCritical) {
    return "CRITICO";
  } else if (currentTemp > 25.0 || (currentHumidity >= 70.0 && currentHumidity <= 75.0) || (currentHumidity >= 45.0 && currentHumidity < 50.0)) {
    return "ATENCION";
  } else {
    return "OPTIMO";
  }
}

void sendDataToAPI() {
  if (!wifiConnected) {
    return;
  }
  
  HTTPClient http;
  
  // Send temperature data
  bool tempSuccess = sendTemperatureData();
  delay(100);
  
  // Send humidity data
  bool humiditySuccess = sendHumidityData();
  
  if (tempSuccess && humiditySuccess) {
    Serial.println("Data sent to API successfully");
    // Brief green flash for success
    digitalWrite(LED_GREEN, HIGH);
    delay(100);
    digitalWrite(LED_GREEN, LOW);
  } else {
    Serial.println("Failed to send data to API");
    // Brief red flash for failure
    digitalWrite(LED_RED, HIGH);
    delay(100);
    digitalWrite(LED_RED, LOW);
  }
}

bool sendTemperatureData() {
  HTTPClient http;
  String url = String(deviceConfig.apiURL) + "/temperatura/";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  // Create JSON payload with Lima timezone
  StaticJsonDocument<300> doc;
  doc["Temperatura"] = currentTemp;
  doc["Sensor_id"] = deviceConfig.sensorID;
  
  String timestamp = getCurrentTimestamp();
  if (timestamp.length() > 0) {
    doc["fecha"] = timestamp;
  }
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  Serial.print("Sending temperature data: ");
  Serial.println(jsonString);
  
  int httpResponseCode = http.POST(jsonString);
  
  bool success = false;
  if (httpResponseCode == 200) {
    success = true;
    Serial.println("Temperature data sent successfully");
  } else {
    Serial.printf("Temperature API error: %d\n", httpResponseCode);
  }
  
  http.end();
  return success;
}

bool sendHumidityData() {
  HTTPClient http;
  String url = String(deviceConfig.apiURL) + "/humedad/";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  // Create JSON payload with Lima timezone
  StaticJsonDocument<300> doc;
  doc["Humedad"] = currentHumidity;
  doc["Sensor_id"] = deviceConfig.sensorID;
  
  String timestamp = getCurrentTimestamp();
  if (timestamp.length() > 0) {
    doc["fecha"] = timestamp;
  }
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  Serial.print("Sending humidity data: ");
  Serial.println(jsonString);
  
  int httpResponseCode = http.POST(jsonString);
  
  bool success = false;
  if (httpResponseCode == 200) {
    success = true;
    Serial.println("Humidity data sent successfully");
  } else {
    Serial.printf("Humidity API error: %d\n", httpResponseCode);
  }
  
  http.end();
  return success;
}

void testOutputs() {
  Serial.println("Testing outputs...");
  
  // Test LEDs
  digitalWrite(LED_RED, HIGH);
  delay(300);
  digitalWrite(LED_RED, LOW);
  
  digitalWrite(LED_YELLOW, HIGH);
  delay(300);
  digitalWrite(LED_YELLOW, LOW);
  
  digitalWrite(LED_GREEN, HIGH);
  delay(300);
  digitalWrite(LED_GREEN, LOW);
  
  // Test buzzer
  digitalWrite(BUZZER_PIN, HIGH);
  delay(200);
  digitalWrite(BUZZER_PIN, LOW);
  
  Serial.println("Output test complete");
}