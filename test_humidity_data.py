#!/usr/bin/env python3
"""
Test script to simulate humidity and temperature sensor data
Perfect for testing your humidity monitoring system before getting real sensors!

Usage:
    python3 test_humidity_data.py
    
This will simulate realistic bakery environment data:
- Temperature: 18-28°C (typical bakery range)
- Humidity: 40-75% (bread storage optimal range)
"""

import requests
import random
import time
import json
from datetime import datetime

# Your API configuration
API_URL = "http://127.0.0.1:8000"

# Simulate realistic bakery conditions
def get_realistic_sensor_data():
    """Generate realistic bakery sensor data"""
    
    # Base conditions
    base_temp = 22.0  # 22°C base temperature
    base_humidity = 55.0  # 55% base humidity
    
    # Add realistic variations
    temp_variation = random.uniform(-4, 6)  # ±4-6°C variation
    humidity_variation = random.uniform(-15, 20)  # ±15-20% variation
    
    # Add some correlation (higher temp = lower humidity, usually)
    correlation_factor = -0.5
    humidity_variation += temp_variation * correlation_factor
    
    temperature = round(base_temp + temp_variation, 1)
    humidity = round(base_humidity + humidity_variation, 1)
    
    # Keep within realistic bounds
    temperature = max(16, min(32, temperature))  # 16-32°C
    humidity = max(30, min(80, humidity))  # 30-80%
    
    return temperature, humidity

def simulate_bakery_scenarios():
    """Simulate different bakery scenarios"""
    scenarios = [
        {
            "name": "Normal Storage",
            "temp_range": (20, 25),
            "humidity_range": (45, 65),
            "probability": 0.6
        },
        {
            "name": "Hot Oven Area", 
            "temp_range": (26, 30),
            "humidity_range": (35, 50),
            "probability": 0.2
        },
        {
            "name": "Humid Day",
            "temp_range": (22, 26),
            "humidity_range": (65, 75),
            "probability": 0.15
        },
        {
            "name": "Cold Storage",
            "temp_range": (16, 20),
            "humidity_range": (50, 70),
            "probability": 0.05
        }
    ]
    
    # Choose scenario based on probability
    rand = random.random()
    cumulative = 0
    
    for scenario in scenarios:
        cumulative += scenario["probability"]
        if rand <= cumulative:
            temp = round(random.uniform(*scenario["temp_range"]), 1)
            humidity = round(random.uniform(*scenario["humidity_range"]), 1)
            return temp, humidity, scenario["name"]
    
    # Fallback to normal
    return 22.0, 55.0, "Normal"

def send_sensor_data(sensor_id, temperature, humidity, location="Test"):
    """Send temperature and humidity data to your API"""
    
    success_count = 0
    
    # Send temperature data
    try:
        temp_response = requests.post(f"{API_URL}/temperatura/", json={
            "Temperatura": temperature,
            "Sensor_id": sensor_id
        }, timeout=5)
        
        if temp_response.status_code == 200:
            success_count += 1
            print(f"✅ Temperatura enviada: {temperature}°C")
        else:
            print(f"❌ Error enviando temperatura: {temp_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión temperatura: {e}")
    
    # Send humidity data  
    try:
        hum_response = requests.post(f"{API_URL}/humedad/", json={
            "Humedad": humidity,
            "Sensor_id": sensor_id
        }, timeout=5)
        
        if hum_response.status_code == 200:
            success_count += 1
            print(f"✅ Humedad enviada: {humidity}%")
        else:
            print(f"❌ Error enviando humedad: {hum_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión humedad: {e}")
    
    return success_count == 2

def check_api_connection():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_URL}/sensores/", timeout=5)
        if response.status_code == 200:
            sensors = response.json()
            print(f"✅ API conectada. Sensores disponibles: {len(sensors)}")
            return True, sensors
        else:
            print(f"❌ API respondió con código: {response.status_code}")
            return False, []
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar a la API: {e}")
        print("🔧 Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
        return False, []

def main():
    """Main simulation function"""
    print("🍞 Simulador de Datos de Sensores - Panadería")
    print("=" * 50)
    
    # Check API connection
    connected, sensors = check_api_connection()
    if not connected:
        return
    
    if not sensors:
        print("⚠️  No hay sensores registrados. Crea un sensor primero en la interfaz web.")
        return
    
    # Show available sensors
    print("📡 Sensores disponibles:")
    for sensor in sensors:
        print(f"   ID: {sensor['idSensores']} - {sensor['nombre']} ({sensor['descripcion']})")
    
    # Use first sensor for demo
    sensor_id = sensors[0]['idSensores']
    sensor_name = sensors[0]['nombre']
    
    print(f"\n🎯 Usando sensor: {sensor_name} (ID: {sensor_id})")
    print("⏰ Enviando datos cada 15 segundos...")
    print("🛑 Presiona Ctrl+C para detener\n")
    
    reading_count = 0
    
    try:
        while True:
            reading_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Generate data using scenarios
            temperature, humidity, scenario = simulate_bakery_scenarios()
            
            print(f"📊 Lectura #{reading_count} [{timestamp}] - Escenario: {scenario}")
            
            # Send data to API
            success = send_sensor_data(sensor_id, temperature, humidity)
            
            if success:
                # Provide bakery-specific insights
                if humidity < 45:
                    print("   ⚠️  Humedad baja - riesgo de pan seco")
                elif humidity > 70:
                    print("   ⚠️  Humedad alta - riesgo de moho")
                else:
                    print("   ✅ Condiciones óptimas para almacenamiento")
                    
                if temperature > 28:
                    print("   🔥 Temperatura alta - verificar ventilación")
                elif temperature < 18:
                    print("   🧊 Temperatura baja - verificar calefacción")
            
            print(f"   💾 Ve los datos en: http://localhost:3000/humedad.html")
            print()
            
            # Wait before next reading
            time.sleep(15)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Simulación detenida después de {reading_count} lecturas")
        print("📈 Revisa el dashboard para ver todos los datos generados!")

if __name__ == "__main__":
    main()