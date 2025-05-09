import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import pytz
from config import *
from soil_sensor import SoilSensorData

class GatewayMQTT:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.sensor = SoilSensorData()
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code: {rc}")
        # Subscribe to soil sensor topic
        self.client.subscribe(self.sensor.topic)
        print(f"Subscribed to topic: {self.sensor.topic}")
        
    def on_disconnect(self, client, userdata, rc):
        print(f"Disconnected from MQTT broker with result code: {rc}")
        
    def on_message(self, client, userdata, msg):
        try:
            # Parse sensor data
            sensor_data = self.sensor.parse_sensor_data(msg.payload.decode())
            if sensor_data:
                # Format and print sensor data
                print(self.sensor.format_sensor_data(sensor_data))
        except Exception as e:
            print(f"Error processing message: {e}")
        
    def connect(self):
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")
            
    def send_stats(self):
        while True:
            try:
                # Get current UTC time
                utc_time = datetime.now(pytz.UTC)
                
                # Create stats message
                stats_message = {
                    "gatewayId": GATEWAY_ID,
                    "time": utc_time.isoformat()
                }
                
                # Publish message
                self.client.publish(STATS_TOPIC, json.dumps(stats_message))
                print(f"Sent stats message: {stats_message}")
                
                # Wait for next interval
                time.sleep(STATS_INTERVAL)
                
            except Exception as e:
                print(f"Error sending stats: {e}")
                time.sleep(5)  # Wait before retrying
                
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == "__main__":
    gateway = GatewayMQTT()
    gateway.connect()
    
    try:
        gateway.send_stats()
    except KeyboardInterrupt:
        print("Stopping gateway...")
        gateway.disconnect() 