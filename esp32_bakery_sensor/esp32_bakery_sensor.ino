#include "DHT.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

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

// --- WiFi Configuration ---
const char* ssid = "AlvaroPhone";  // Simplified iPhone hotspot name
const char* password = "Alvarooo";

// --- API Configuration ---
const char* apiURL = "http://192.168.18.91:8000";  // Your Mac's IP address
const int sensorID = 1;  // Replace with your sensor ID from database

// --- Alert Thresholds ---
const float TEMP_CRITICAL_HIGH = 28.0;   // °C
const float TEMP_CRITICAL_LOW = 16.0;    // °C
const float HUMIDITY_CRITICAL_HIGH = 70.0; // %
const float HUMIDITY_CRITICAL_LOW = 45.0;  // %

// --- Create Objects ---
DHT dht(DHTPIN, DHTTYPE);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// --- Global Variables ---
bool wifiConnected = false;
unsigned long lastSensorRead = 0;
unsigned long lastAPICall = 0;
const unsigned long SENSOR_INTERVAL = 2000;  // Read sensor every 2 seconds
const unsigned long API_INTERVAL = 15000;    // Send to API every 15 seconds

float currentTemp = 0.0;
float currentHumidity = 0.0;
bool sensorError = false;

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 Bakery Sensor System Starting...");

  // Initialize hardware
  initializePins();
  initializeDisplay();
  initializeSensor();
  
  // Connect to WiFi
  connectToWiFi();
  
  Serial.println("System initialized successfully!");
}

void loop() {
  // Read sensor data
  if (millis() - lastSensorRead >= SENSOR_INTERVAL) {
    readSensorData();
    updateDisplay();
    updateAlerts();
    lastSensorRead = millis();
  }
  
  // Send data to API
  if (millis() - lastAPICall >= API_INTERVAL && wifiConnected && !sensorError) {
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
  
  // Test sensor
  float testTemp = dht.readTemperature();
  if (isnan(testTemp)) {
    Serial.println("DHT22 sensor not responding!");
    sensorError = true;
  } else {
    Serial.println("DHT22 sensor initialized successfully");
    sensorError = false;
  }
}

void connectToWiFi() {
  setLEDStatus("connecting");
  
  Serial.print("Connecting to WiFi network: ");
  Serial.println(ssid);
  
  // Try to improve compatibility
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  
  WiFi.begin(ssid, password);
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
  display.print("Panaderia Sensor");
  
  // WiFi Status
  display.setCursor(90, 0);
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
  } else if (currentTemp > 25.0 || currentHumidity > 65.0 || currentHumidity < 50.0) {
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
  } else if (currentTemp > 25.0 || currentHumidity > 65.0 || currentHumidity < 50.0) {
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
  String url = String(apiURL) + "/temperatura/";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["Temperatura"] = currentTemp;
  doc["Sensor_id"] = sensorID;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
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
  String url = String(apiURL) + "/humedad/";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["Humedad"] = currentHumidity;
  doc["Sensor_id"] = sensorID;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
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