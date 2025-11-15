import json
import paho.mqtt.client as mqtt
from typing import Dict, Any
from app.config import settings


class MQTTPublisher:
    def __init__(self):
        self.client = mqtt.Client()
        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        self.client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
    
    def publish_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Publish an alert to the MQTT alerts topic."""
        try:
            payload = json.dumps(alert_data)
            result = self.client.publish(settings.MQTT_TOPIC_ALERTS, payload)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Error publishing alert: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.client.disconnect()

