import paho.mqtt.client as mqtt
import json
import time
import sys

# Configuración MQTT
MQTT_BROKER = "xxxxxxxx"
MQTT_PORT = 1883
MQTT_CMD_TOPIC = "motor/comando"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Conectado al broker MQTT")
    else:
        print(f"❌ Error de conexión, código: {rc}")

def enviar_comando(client, comando, velocidad=200):
    """Envía un comando al motor"""
    mensaje = {"comando": comando}
    if comando != "stop":
        mensaje["velocidad"] = velocidad
    client.publish(MQTT_CMD_TOPIC, json.dumps(mensaje))
    print(f"📤 Comando enviado: {mensaje}")

def clear_screen():
    """Limpia la pantalla"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_menu():
    """Muestra el menú en pantalla"""
    print("\n" + "="*40)
    print("🎮 CONTROL DEL MOTOR DC")
    print("="*40)
    print("1. 🔴 ENCENDER motor")
    print("2. ⚫ APAGAR motor")
    print("3. 🧪 Prueba rápida (adelante → stop → atrás)")
    print("4. ❌ SALIR")
    print("="*40)

# Crear cliente
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect

print(f"🔌 Conectando a {MQTT_BROKER}:{MQTT_PORT}...")

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    time.sleep(1)
    
    print("✅ Conectado. Esperando comandos...")
    
    while True:
        mostrar_menu()
        opcion = input("\n👉 Selecciona una opción (1-4): ").strip()
        
        if opcion == '1':
            print("\n🔴 ENCENDIENDO motor...")
            enviar_comando(client, "forward", 200)
            
        elif opcion == '2':
            print("\n⚫ APAGANDO motor...")
            enviar_comando(client, "stop")
            
        elif opcion == '3':
            print("\n🧪 Prueba rápida:")
            print("   Adelante → 3 segundos")
            enviar_comando(client, "forward", 200)
            time.sleep(3)
            
            print("   Stop → 2 segundos")
            enviar_comando(client, "stop")
            time.sleep(2)
            
            print("   Reversa → 3 segundos")
            enviar_comando(client, "backward", 150)
            time.sleep(3)
            
            print("   Stop final")
            enviar_comando(client, "stop")
            
        elif opcion == '4':
            print("\n👋 Saliendo...")
            break
            
        else:
            print("\n❌ Opción inválida. Intenta de nuevo.")
        
        time.sleep(0.5)
        input("\nPresiona Enter para continuar...")
        clear_screen()
    
except ConnectionRefusedError:
    print("\n❌ ERROR: No se pudo conectar al broker MQTT")
    print("1. Verifica que Mosquitto esté corriendo")
    print("2. Verifica la IP en config.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")

finally:
    client.loop_stop()
    client.disconnect()
    print("🔌 Desconectado")