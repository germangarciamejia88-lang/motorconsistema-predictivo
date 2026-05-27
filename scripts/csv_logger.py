import csv
import os
import json
from datetime import datetime
import pandas as pd
from config import CSV_FILE, COLUMNAS, BUFFER_SIZE, DATA_DIR

class CSVLogger:
    def __init__(self, filename=CSV_FILE):
        self.filename = filename
        self.buffer = []
        self.buffer_size = BUFFER_SIZE
        self.init_csv()
    
    def init_csv(self):
        """Crea el archivo CSV con encabezados si no existe"""
        # Crear directorio si no existe
        os.makedirs(DATA_DIR, exist_ok=True)
        
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(COLUMNAS)
            print(f"✅ Archivo CSV creado: {self.filename}")
        else:
            print(f"📁 Usando archivo existente: {self.filename}")
    
    def save_data(self, accel_x, accel_y, accel_z, estado_real="unknown", 
                  prediccion="", confianza=""):
        """Guarda un registro de datos"""
        record = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            'accel_x': accel_x,
            'accel_y': accel_y,
            'accel_z': accel_z,
            'estado_real': estado_real,
            'prediccion': prediccion,
            'confianza': confianza
        }
        
        self.buffer.append(record)
        
        # Guardar cuando el buffer se llena
        if len(self.buffer) >= self.buffer_size:
            self.flush()
    
    def save_from_mqtt(self, payload, prediction=None):
        """Guarda datos recibidos de MQTT"""
        try:
            # Parsear JSON
            if isinstance(payload, str):
                data = json.loads(payload)
            else:
                data = payload
            
            # Extraer predicción si existe
            prediccion = prediction.get('estado', '') if prediction else ''
            confianza = prediction.get('confianza', '') if prediction else ''
            
            # Guardar datos
            self.save_data(
                data.get('accel_x', 0),
                data.get('accel_y', 0),
                data.get('accel_z', 0),
                data.get('estado', 'unknown'),
                prediccion,
                confianza
            )
            return True
        except json.JSONDecodeError as e:
            print(f"⚠️ Error JSON: {e}")
            return False
        except Exception as e:
            print(f"⚠️ Error guardando: {e}")
            return False
    
    def flush(self):
        """Guarda el buffer en CSV"""
        if not self.buffer:
            return
        
        try:
            with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for record in self.buffer:
                    row = [record[col] for col in COLUMNAS]
                    writer.writerow(row)
            
            print(f"💾 Guardados {len(self.buffer)} registros en {self.filename}")
            self.buffer = []
        except Exception as e:
            print(f"❌ Error escribiendo CSV: {e}")
    
    def force_save(self):
        """Fuerza el guardado de cualquier dato pendiente"""
        self.flush()
    
    def get_dataframe(self):
        """Carga todos los datos como DataFrame"""
        try:
            return pd.read_csv(self.filename)
        except:
            return pd.DataFrame(columns=COLUMNAS)
    
    def get_stats(self):
        """Obtiene estadísticas del archivo"""
        df = self.get_dataframe()
        stats = {
            "total_records": len(df),
            "columns": list(df.columns),
            "file_size_kb": os.path.getsize(self.filename) / 1024 if os.path.exists(self.filename) else 0
        }
        
        if len(df) > 0:
            stats["last_timestamp"] = df['timestamp'].iloc[-1]
        
        return stats
    
    def get_last_n(self, n=10):
        """Obtiene los últimos n registros"""
        df = self.get_dataframe()
        return df.tail(n)
