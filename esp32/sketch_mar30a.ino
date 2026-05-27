#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ========= CONFIGURACIÓN ADXL345 =========
#define ADXL345_ADDRESS 0x53
#define ADXL345_REG_DEVID 0x00
#define ADXL345_REG_POWER_CTL 0x2D
#define ADXL345_REG_DATAX0 0x32

// ========= CONFIGURACIÓN WiFi =========
const char* ssid = "xxxxxxx";
const char* password = "xxxxxxx";
const char* mqtt_server = "xxxxxxx";
const int mqtt_port = 1883;

// ========= TÓPICOS MQTT =========
const char* mqtt_topic_vibracion = "motor/vibracion";
const char* mqtt_topic_comando = "motor/comando";

// ========= CONFIGURACIÓN DEL MOTOR =========
const int motorIN1 = 25;   // Dirección 1
const int motorIN2 = 26;   // Dirección 2

// ========= OBJETOS GLOBALES =========
WiFiClient espClient;
PubSubClient client(espClient);

bool adxlOK = false;
unsigned long lastVibrationRead = 0;
const long vibrationInterval = 1000;

float accel_x = 0, accel_y = 0, accel_z = 0;

// ========= SETUP =========
void setup() {
  Serial.begin(115200);
  delay(100);
  
  Serial.println("\n🚀 Iniciando sistema con ADXL345...");
  
  // 1. Configurar motor
  pinMode(motorIN1, OUTPUT);
  pinMode(motorIN2, OUTPUT);
  stopMotor();
  Serial.println("✅ Motor configurado");
  
  // 2. Inicializar ADXL345
  Wire.begin(21, 22); // SDA=21, SCL=22
  
  if (initADXL345()) {
    Serial.println("✅ ADXL345 detectado");
    adxlOK = true;
  } else {
    Serial.println("⚠️ ADXL345 no detectado - Sistema funcionará sin vibración");
  }
  
  // 3. Conectar WiFi
  Serial.print("📡 Conectando WiFi");
  WiFi.begin(ssid, password);
  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 20) {
    delay(500);
    Serial.print(".");
    intentos++;
  }
  Serial.println();
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("✅ WiFi conectada - IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("⚠️ WiFi no conectado");
  }
  
  // 4. Configurar MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  if (WiFi.status() == WL_CONNECTED) {
    reconnectMQTT();
  }
  
  Serial.println("\n✅ Sistema listo!");
  Serial.println("========================================\n");
}

// ========= INICIALIZAR ADXL345 =========
bool initADXL345() {
  // Verificar Device ID
  Wire.beginTransmission(ADXL345_ADDRESS);
  Wire.write(ADXL345_REG_DEVID);
  Wire.endTransmission(false);
  Wire.requestFrom(ADXL345_ADDRESS, (uint8_t)1);
  
  if (!Wire.available()) return false;
  
  byte deviceId = Wire.read();
  if (deviceId != 0xE5) return false;
  
  // Modo medición
  Wire.beginTransmission(ADXL345_ADDRESS);
  Wire.write(ADXL345_REG_POWER_CTL);
  Wire.write(0x08);
  Wire.endTransmission();
  
  // Rango ±16g
  Wire.beginTransmission(ADXL345_ADDRESS);
  Wire.write(0x31);
  Wire.write(0x0B);
  Wire.endTransmission();
  
  return true;
}

// ========= LEER ADXL345 =========
void readADXL345() {
  Wire.beginTransmission(ADXL345_ADDRESS);
  Wire.write(ADXL345_REG_DATAX0);
  Wire.endTransmission(false);
  Wire.requestFrom(ADXL345_ADDRESS, (uint8_t)6);
  
  if (Wire.available() >= 6) {
    int16_t x = Wire.read() | (Wire.read() << 8);
    int16_t y = Wire.read() | (Wire.read() << 8);
    int16_t z = Wire.read() | (Wire.read() << 8);
    
    accel_x = x / 256.0;
    accel_y = y / 256.0;
    accel_z = z / 256.0;
  }
}

// ========= FUNCIONES DEL MOTOR =========
void motorAdelante(int velocidad) {
  Serial.printf("🚀 Motor ADELANTE (vel: %d)\n", velocidad);
  digitalWrite(motorIN1, HIGH);
  digitalWrite(motorIN2, LOW);
}

void motorReversa(int velocidad) {
  Serial.printf("🔻 Motor REVERSA (vel: %d)\n", velocidad);
  digitalWrite(motorIN1, LOW);
  digitalWrite(motorIN2, HIGH);
}

void stopMotor() {
  Serial.println("⏹️ Motor DETENIDO");
  digitalWrite(motorIN1, LOW);
  digitalWrite(motorIN2, LOW);
}

// ========= CALLBACK MQTT =========
void callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.print("📩 Comando recibido: ");
  Serial.println(message);
  
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, message);
  
  if (!error) {
    const char* comando = doc["comando"];
    
    if (strcmp(comando, "forward") == 0) {
      motorAdelante(200);
    } 
    else if (strcmp(comando, "backward") == 0) {
      motorReversa(150);
    }
    else if (strcmp(comando, "stop") == 0) {
      stopMotor();
    }
  }
}

// ========= ENVIAR DATOS DE VIBRACIÓN =========
void sendVibrationData() {
  if (!adxlOK) return;
  if (!client.connected()) return;
  
  readADXL345();
  
  float magnitud = sqrt(accel_x*accel_x + accel_y*accel_y + accel_z*accel_z);
  
  StaticJsonDocument<200> doc;
  doc["accel_x"] = accel_x;
  doc["accel_y"] = accel_y;
  doc["accel_z"] = accel_z;
  doc["magnitud"] = magnitud;
  
  char buffer[256];
  serializeJson(doc, buffer);
  
  client.publish(mqtt_topic_vibracion, buffer);
  
  Serial.printf("📤 X:%.2f Y:%.2f Z:%.2f | Mag:%.2f\n", 
                accel_x, accel_y, accel_z, magnitud);
}

// ========= CONEXIÓN MQTT =========
void reconnectMQTT() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  String clientId = "ESP32_ADXL345_" + String(random(0xffff), HEX);
  Serial.print("Conectando MQTT...");
  
  if (client.connect(clientId.c_str())) {
    Serial.println(" ✅");
    client.subscribe(mqtt_topic_comando);
    Serial.print("   Suscrito a: ");
    Serial.println(mqtt_topic_comando);
  } else {
    Serial.print(" ❌ error: ");
    Serial.println(client.state());
  }
}

// ========= LOOP PRINCIPAL =========
void loop() {
  if (WiFi.status() == WL_CONNECTED && !client.connected()) {
    reconnectMQTT();
  }
  
  if (client.connected()) {
    client.loop();
  }
  
  // Enviar datos de vibración cada segundo
  if (adxlOK && client.connected() && (millis() - lastVibrationRead >= vibrationInterval)) {
    sendVibrationData();
    lastVibrationRead = millis();
  }
  
  delay(10);
}