import random
from datetime import datetime
import time

class Device:
    def __init__(self, name, power):
        self.name = name
        self.power = power
        self.is_on = False
        self.effect_temp = 0
        self.effect_humidity = 0
        self.effect_co2 = 0
    
    def turn_on(self):
        self.is_on = True
        return self
    
    def turn_off(self):
        self.is_on = False
        return self
    
    def get_effects(self):
        if self.is_on:
            return {
                'temperature': self.effect_temp,
                'humidity': self.effect_humidity,
                'co2': self.effect_co2
            }
        return {'temperature': 0, 'humidity': 0, 'co2': 0}

class Heater(Device):
    def __init__(self, name="Обогреватель", power=0.5):
        super().__init__(name, power)
        self.effect_temp = 2.5 * power
        self.effect_humidity = -3.0 * power
        self.effect_co2 = 0

class AirConditioner(Device):
    def __init__(self, name="Кондиционер", power=0.7):
        super().__init__(name, power)
        self.effect_temp = -4.0 * power
        self.effect_humidity = -5.0 * power
        self.effect_co2 = 0

class ColdWindow(Device):
    def __init__(self, name="Окно (холод)", power=0.6):
        super().__init__(name, power)
        self.effect_temp = -2.5 * power
        self.effect_humidity = random.uniform(-5, 5) * power
        self.effect_co2 = -180.0 * power

class HotWindow(Device):
    def __init__(self, name="Окно (жара)", power=0.5):
        super().__init__(name, power)
        self.effect_temp = 1.5 * power
        self.effect_humidity = random.uniform(-10, 0) * power
        self.effect_co2 = -150.0 * power

class Dehumidifier(Device):
    def __init__(self, name="Осушитель", power=0.6):
        super().__init__(name, power)
        self.effect_temp = 1.0 * power
        self.effect_humidity = -12.0 * power
        self.effect_co2 = 0

class Humidifier(Device):
    def __init__(self, name="Увлажнитель", power=0.6):
        super().__init__(name, power)
        self.effect_temp = 0.3 * power
        self.effect_humidity = 10.0 * power
        self.effect_co2 = 0

class SensorSimulator:
    def __init__(self):
        self.temperature = random.uniform(20.0, 24.0)
        self.humidity = random.uniform(40.0, 60.0)
        self.co2 = random.uniform(450.0, 650.0)
        
        self.devices = {
            'heater': Heater("Обогреватель", random.uniform(0.4, 0.8)),
            'ac': AirConditioner("Кондиционер", random.uniform(0.5, 0.9)),
            'cold_window': ColdWindow("Окно (холод)", random.uniform(0.3, 0.7)),
            'hot_window': HotWindow("Окно (жара)", random.uniform(0.3, 0.6)),
            'dehumidifier': Dehumidifier("Осушитель", random.uniform(0.4, 0.7)),
            'humidifier': Humidifier("Увлажнитель", random.uniform(0.4, 0.7))
        }
        
        self.counter = 0
        self.hour = datetime.now().hour
    
    def auto_control_devices(self):
        if self.counter % 15 == 0:
            current_hour = datetime.now().hour
            is_daytime = 6 <= current_hour < 22
            
            if self.temperature < 19.0:
                self.devices['heater'].turn_on()
                self.devices['ac'].turn_off()
                if random.random() < 0.3:
                    self.devices['cold_window'].turn_off()
            elif self.temperature > 27.0:
                self.devices['ac'].turn_on()
                self.devices['heater'].turn_off()
                if random.random() < 0.4 and is_daytime:
                    self.devices['hot_window'].turn_on()
            else:
                if random.random() < 0.2:
                    self.devices['heater'].turn_off()
                if random.random() < 0.2:
                    self.devices['ac'].turn_off()
            
            if self.humidity < 35.0:
                self.devices['humidifier'].turn_on()
                self.devices['dehumidifier'].turn_off()
            elif self.humidity > 65.0:
                self.devices['dehumidifier'].turn_on()
                self.devices['humidifier'].turn_off()
            else:
                if random.random() < 0.3:
                    self.devices['humidifier'].turn_off()
                if random.random() < 0.3:
                    self.devices['dehumidifier'].turn_off()
            
            if self.co2 > 900.0:
                if self.temperature < 22.0:
                    self.devices['cold_window'].turn_on()
                else:
                    self.devices['hot_window'].turn_on()
            elif self.co2 < 500.0:
                if random.random() < 0.4:
                    self.devices['cold_window'].turn_off()
                    self.devices['hot_window'].turn_off()
    
    def calculate_device_effects(self):
        total = {'temperature': 0, 'humidity': 0, 'co2': 0}
        
        for device in self.devices.values():
            effects = device.get_effects()
            total['temperature'] += effects['temperature']
            total['humidity'] += effects['humidity']
            total['co2'] += effects['co2']
        
        return total
    
    def get_readings(self):
        self.auto_control_devices()
        
        device_effects = self.calculate_device_effects()
        
        temp_change = random.uniform(-0.15, 0.15)
        humidity_change = random.uniform(-0.8, 0.8)
        co2_change = random.uniform(-8, 8)
        
        temp_change += device_effects['temperature'] * 0.03
        humidity_change += device_effects['humidity'] * 0.03
        co2_change += device_effects['co2'] * 0.03
        
        self.temperature += temp_change
        self.humidity += humidity_change
        self.co2 += co2_change
        
        self.temperature = max(15.0, min(32.0, self.temperature))
        self.humidity = max(25.0, min(85.0, self.humidity))
        self.co2 = max(350.0, min(1500.0, self.co2))
        
        self.counter += 1
        
        active_devices = [d.name for d in self.devices.values() if d.is_on]
        
        return {
            "temperature": round(self.temperature, 1),
            "humidity": round(self.humidity, 1),
            "co2": round(self.co2, 0),
            "timestamp": datetime.now().isoformat(),
            "active_devices": active_devices
        }
    
    def manual_control(self, device_name, state):
        if device_name in self.devices:
            if state:
                self.devices[device_name].turn_on()
            else:
                self.devices[device_name].turn_off()
    
    def get_device_status(self):
        status = {}
        for name, device in self.devices.items():
            status[name] = {
                'name': device.name,
                'is_on': device.is_on,
                'power': device.power
            }
        return status

def get_sensor_data():
    if not hasattr(get_sensor_data, 'sensor'):
        get_sensor_data.sensor = SensorSimulator()
    
    data = get_sensor_data.sensor.get_readings()
    
    return {
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "co2": data["co2"],
        "timestamp": data["timestamp"]
    }

def run_simulation(seconds=30):
    sensor = SensorSimulator()
    
    print("Темп: °C | Влаж: % | CO₂: ppm | Устройства")
    print("-" * 60)
    
    try:
        for i in range(seconds):
            data = sensor.get_readings()
            
            temp = data['temperature']
            hum = data['humidity']
            co2 = data['co2']
            devices = data['active_devices']
            
            device_icons = []
            for dev in devices:
                if "Обогреватель" in dev:
                    device_icons.append("🔥")
                elif "Кондиционер" in dev:
                    device_icons.append("❄️")
                elif "Окно (холод)" in dev:
                    device_icons.append("🪟❄️")
                elif "Окно (жара)" in dev:
                    device_icons.append("🪟🔥")
                elif "Осушитель" in dev:
                    device_icons.append("🌀")
                elif "Увлажнитель" in dev:
                    device_icons.append("💧")
            
            device_str = " ".join(device_icons) if device_icons else "-"
            
            print(f"{i+1:3d}. {temp:5.1f}°C | {hum:5.1f}% | {co2:6.0f} ppm | {device_str}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nСимуляция остановлена")

if __name__ == "__main__":
    run_simulation(30)