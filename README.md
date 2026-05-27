# 🚀 Control Predictivo de Motor con Acelerometro ESP32 + MQTT


## 📋 Descripción del Proyecto

Este proyecto implementa un **sistema de monitoreo y control predictivo** para un motor eléctrico utilizando un **ESP32**, un **acelerómetro MPU6050** (o similar), un **puente H** para control del motor y comunicación **MQTT** para transmitir datos en tiempo real.

El sistema captura las aceleraciones en los ejes **X, Y, Z** generadas por la vibración del motor, las publica vía MQTT, y permite el **encendido/apagado remoto** del motor. Los datos recibidos se almacenan automáticamente en archivos **CSV** para su posterior análisis predictivo (detección de fallos, mantenimiento predictivo, etc.).

---

## 🎯 Objetivos

- ✅ Adquirir datos de vibración del motor mediante acelerómetro.
- ✅ Transmitir datos por **MQTT** desde el ESP32 a una computadora central.
- ✅ Almacenar los datos en **CSV** estructurado (timestamp, X, Y, Z).
- ✅ Controlar el motor (ON/OFF) de forma remota vía WIFFI.
- ✅ Generar base de datos para **modelos predictivos** de fallos.

---

## 🛠️ Tecnologías Utilizadas

| Componente       | Tecnología                           |
|------------------|--------------------------------------|
| Microcontrolador | ESP32                                |
| Acelerómetro     | ADXL345                              |
| Control Motor    | Puente H L298N o L293D               |
| Motor            | DC Motor 6-12V                       |
| Comunicación     | MQTT (Mosquitto broker)              |
| Lenguajes        | Python, C++ (Arduino)                |
| Almacenamiento   | CSV (pandas)                         |
| Procesamiento    | Filtros pasa-altas, análisis RMS     |

---

## 📁 Estructura del Repositorio

---

## 🔌 Diagrama de Conexión


<img width="1168" height="490" alt="WhatsApp Image 2026-05-25 at 9 59 24 PM" src="https://github.com/user-attachments/assets/27b6269a-131f-4d1f-95e7-2f74b06a4571" />



### Conexiones principales:

| Componente       | ESP32 Pin     |
|------------------|---------------|
| Acelerómetro SDA | GPIO 21       |
| Acelerómetro SCL | GPIO 22       |
| Puente H IN1     | GPIO 25       |
| Puente H IN2     | GPIO 26       |
| Motor (+)        | Puente H OUT1 |
| Motor (-)        | Puente H OUT2 |

---

## 📡 Comunicación MQTT

**Tópicos utilizados:**

| Tópico                        | Dirección      | Descripción                        |
|-------------------------------|----------------|------------------------------------|
| `motor/acelerometro/datos`    | ESP32 → Broker | Envía `X,Y,Z` en formato CSV       |
| `motor/control/comando`       | Broker → ESP32 | Recibe `ON` / `OFF` para el motor  |
| `motor/estado`                | ESP32 → Broker | Publica estado actual del motor    |

**Ejemplo de mensaje publicado por el ESP32:**
```json
{
  "timestamp": 1698765432,
  "X": 0.12,
  "Y": -0.03,
  "Z": 9.81
}
