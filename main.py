import os
import sys
import pandas as pd

# Agregar scripts al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from config import CSV_FILE, DATA_DIR, MODELS_DIR
from mqtt_receiver import MQTTReceiver
from realtime_classifier import RealTimeClassifier
from knn_model import KNNPredictor

def clear_screen():
    """Limpia la pantalla"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_header():
    """Muestra el encabezado del sistema"""
    print("="*60)
    print("     SISTEMA DE MANTENIMIENTO PREDICTIVO")
    print("     Motor DC + MPU6050 + MQTT + KNN")
    print("="*60)
    print(f"📁 Datos: {CSV_FILE}")
    print(f"📁 Modelos: {MODELS_DIR}")
    print("="*60)

def show_stats():
    """Muestra estadísticas de los datos"""
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        print(f"\n📊 ESTADÍSTICAS DE DATOS")
        print("-"*40)
        print(f"Total registros: {len(df)}")
        print(f"Columnas: {list(df.columns)}")
        
        if len(df) > 0:
            print(f"\nÚltimos 5 registros:")
            print(df.tail(5).to_string())
            
            if 'prediccion' in df.columns:
                print(f"\nDistribución de predicciones:")
                pred_counts = df['prediccion'].value_counts()
                for estado, count in pred_counts.items():
                    print(f"  {estado}: {count}")
        
        # Tamaño del archivo
        size_kb = os.path.getsize(CSV_FILE) / 1024
        print(f"\n💾 Tamaño del archivo: {size_kb:.2f} KB")
    else:
        print("\n⚠️ No hay datos aún. Ejecuta el receptor primero.")

def main():
    while True:
        clear_screen()
        show_header()
        
        print("\n📋 MENÚ PRINCIPAL")
        print("-"*40)
        print("1. 📡 RECIBIR DATOS (solo guardar, sin ML)")
        print("2. 🤖 CLASIFICAR EN TIEMPO REAL (con KNN)")
        print("3. 🎯 ENTRENAR MODELO (con datos existentes)")
        print("4. 📊 VER ESTADÍSTICAS")
        print("5. 🧪 PROBAR MODELO (con datos sintéticos)")
        print("6. ❌ SALIR")
        print("-"*40)
        
        opcion = input("\n👉 Selecciona una opción (1-6): ").strip()
        
        if opcion == '1':
            clear_screen()
            receiver = MQTTReceiver()
            receiver.start()
            
        elif opcion == '2':
            clear_screen()
            classifier = RealTimeClassifier()
            classifier.start()
            
        elif opcion == '3':
            clear_screen()
            print("🎯 ENTRENAMIENTO DE MODELO")
            print("-"*40)
            predictor = KNNPredictor()
            if predictor.train():
                input("\n✅ Entrenamiento completado. Presiona Enter para continuar...")
            else:
                input("\n❌ Error en entrenamiento. Presiona Enter para continuar...")
                
        elif opcion == '4':
            clear_screen()
            show_stats()
            input("\nPresiona Enter para continuar...")
            
        elif opcion == '5':
            clear_screen()
            print("🧪 PRUEBA DEL MODELO")
            print("-"*40)
            print("Generando datos sintéticos para probar el modelo...")
            
            import numpy as np
            import pandas as pd
            
            # Crear datos de prueba
            test_data = pd.DataFrame({
                'accel_x': [0.1, 0.2, 1.5, 1.8, 3.0, 3.5],
                'accel_y': [0.0, 0.1, 1.2, 1.5, 2.5, 3.0],
                'accel_z': [9.8, 9.9, 11.5, 11.8, 14.0, 14.5]
            })
            
            predictor = KNNPredictor()
            if predictor.load_model():
                print("\n📊 Resultados de prueba:")
                print("-"*40)
                for i, row in test_data.iterrows():
                    result = predictor.predict(row.to_dict())
                    if result:
                        print(f"Dato {i+1}: X={row['accel_x']:.1f} Y={row['accel_y']:.1f} Z={row['accel_z']:.1f}")
                        print(f"  → {result['estado'].upper()} (confianza: {result['confianza']:.2%})")
            else:
                print("⚠️ No hay modelo entrenado. Entrena el modelo primero.")
            
            input("\nPresiona Enter para continuar...")
            
        elif opcion == '6':
            print("\n👋 Saliendo del sistema...")
            break
        else:
            print("\n❌ Opción inválida")
            input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()