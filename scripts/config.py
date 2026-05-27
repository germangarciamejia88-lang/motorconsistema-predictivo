import os

# ========== CONFIGURACIÓN DE RUTAS ==========
# Obtener la carpeta RAIZ del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ========== CONFIGURACIÓN MQTT ==========
MQTT_BROKER = "xxxxxxx"  # Cambiar por IP de tu PC si es remoto
MQTT_PORT = 1883
MQTT_TOPIC = "motor/vibracion"
MQTT_CLIENT_ID = "python_predictive_system"

# ========== ARCHIVOS ==========
# Usando rutas ABSOLUTAS para evitar problemas
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
CSV_FILE = os.path.join(DATA_DIR, "vibraciones.csv")

# ========== COLUMNAS DEL CSV ==========
COLUMNAS = ["timestamp", "accel_x", "accel_y", "accel_z", "estado_real", "prediccion", "confianza"]

# ========== UMBRALES PARA ETIQUETAS ==========
THRESHOLD_NORMAL = 10.5      # Vibración normal
THRESHOLD_WARNING = 12.0     # Umbral de advertencia

# ========== CONFIGURACIÓN KNN ==========
KNN_NEIGHBORS = 5
KNN_WEIGHTS = 'distance'  # 'uniform' o 'distance'

# ========== CONFIGURACIÓN DE ENTRENAMIENTO ==========
TEST_SIZE = 0.2
RANDOM_STATE = 42

# ========== BUFFER PARA CSV ==========
BUFFER_SIZE = 20  # Guardar cada 5 lecturas (cambiar a 1 para guardado inmediato)

# ========== DEBUG ==========
print(f"📁 Directorio base: {BASE_DIR}")
print(f"📁 Datos se guardan en: {CSV_FILE}")