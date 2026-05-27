import paho.mqtt.client as mqtt
import json
import signal
import sys
from knn_model import KNNPredictor
from csv_logger import CSVLogger
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

class RealTimeClassifier:
    def __init__(self):
        self.predictor = KNNPredictor()
        self.logger = CSVLogger()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.running = True
        
        # Manejar cierre elegante
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Cargar o entrenar modelo
        if not self.predictor.load_model():
            print("🔄 Entrenando modelo automáticamente...")
            if not self.predictor.train():
                print("❌ No se pudo entrenar el modelo")
                sys.exit(1)
    
    def signal_handler(self, sig, frame):
        """Maneja Ctrl+C para guardar datos pendientes"""
        print("\n🛑 Deteniendo clasificador...")
        self.logger.force_save()
        self.running = False
        self.client.disconnect()
        sys.exit(0)
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✅ Conectado al broker MQTT")
            client.subscribe(MQTT_TOPIC)
            print(f"📡 Clasificador activo en: {MQTT_TOPIC}")
        else:
            print(f"❌ Error de conexión: {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)
            
            # Predecir estado
            prediction = self.predictor.predict(data)
            
            if prediction:
                estado = prediction['estado']
                confianza = prediction['confianza']
                
                # Mostrar resultado con colores (símbolos)
                if estado == 'normal':
                    print(f"✅ NORMAL - Confianza: {confianza:.2%}")
                elif estado == 'warning':
                    print(f"⚠️ ADVERTENCIA - Confianza: {confianza:.2%}")
                elif estado == 'failure':
                    print(f"🔴 POSIBLE FALLA - Confianza: {confianza:.2%}")
                
                # Guardar en CSV con predicción
                self.logger.save_from_mqtt(payload, prediction)
            
        except json.JSONDecodeError:
            print(f"⚠️ Error JSON: {payload}")
        except Exception as e:
            print(f"⚠️ Error: {e}")
    
    def start(self):
        """Inicia el clasificador en tiempo real"""
        print("="*50)
        print("🤖 CLASIFICADOR EN TIEMPO REAL - KNN")
        print("="*50)
        print(f"Broker: {MQTT_BROKER}:{MQTT_PORT}")
        print(f"Tópico: {MQTT_TOPIC}")
        print(f"Archivo: {self.logger.filename}")
        print("="*50)
        print("Presiona Ctrl+C para detener\n")
        
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_forever()

if __name__ == "__main__":
    classifier = RealTimeClassifier()
    classifier.start()