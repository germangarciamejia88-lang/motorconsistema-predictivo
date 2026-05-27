import paho.mqtt.client as mqtt
import json
import signal
import sys
from csv_logger import CSVLogger
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

class MQTTReceiver:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.logger = CSVLogger()
        self.running = True
        
        # Manejar cierre elegante
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Maneja Ctrl+C para guardar datos pendientes"""
        print("\n🛑 Deteniendo receptor...")
        self.logger.force_save()
        self.running = False
        self.client.disconnect()
        sys.exit(0)
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✅ Conectado al broker {MQTT_BROKER}:{MQTT_PORT}")
            client.subscribe(MQTT_TOPIC)
            print(f"📡 Suscrito al tópico: {MQTT_TOPIC}")
        else:
            print(f"❌ Error de conexión. Código: {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            print(f"📨 Recibido: {payload}")
            
            # Guardar en CSV
            self.logger.save_from_mqtt(payload)
            
        except json.JSONDecodeError:
            print(f"⚠️ Error: No se pudo parsear JSON: {payload}")
        except Exception as e:
            print(f"⚠️ Error procesando mensaje: {e}")
    
    def start(self):
        """Inicia el cliente MQTT"""
        print("="*50)
        print("🚀 RECEPTOR MQTT - Guardando datos en CSV")
        print("="*50)
        print(f"Broker: {MQTT_BROKER}:{MQTT_PORT}")
        print(f"Tópico: {MQTT_TOPIC}")
        print(f"Archivo: {self.logger.filename}")
        print("="*50)
        print("Presiona Ctrl+C para detener\n")
        
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_forever()

if __name__ == "__main__":
    receiver = MQTTReceiver()
    receiver.start()