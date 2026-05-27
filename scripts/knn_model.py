import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, precision_recall_curve)
from sklearn.preprocessing import StandardScaler
import joblib
import os
import json
from config import (CSV_FILE, THRESHOLD_NORMAL, THRESHOLD_WARNING, 
                    KNN_NEIGHBORS, KNN_WEIGHTS, TEST_SIZE, RANDOM_STATE,
                    MODELS_DIR)

class KNNPredictor:
    def __init__(self):
        self.model = KNeighborsClassifier(
            n_neighbors=KNN_NEIGHBORS,
            weights=KNN_WEIGHTS,
            metric='euclidean',
            n_jobs=-1  # Usar todos los núcleos
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = None
        self.classes_ = None
    
    def calculate_features(self, df):
        """Extrae características de los datos de aceleración"""
        df_features = df.copy()
        
        # Magnitud de vibración (característica principal)
        df_features['magnitud'] = np.sqrt(
            df_features['accel_x']**2 + 
            df_features['accel_y']**2 + 
            df_features['accel_z']**2
        )
        
        # Características estadísticas (ventana de 5)
        if len(df_features) >= 5:
            df_features['mag_rolling_mean'] = df_features['magnitud'].rolling(window=5, min_periods=1).mean()
            df_features['mag_rolling_std'] = df_features['magnitud'].rolling(window=5, min_periods=1).std()
            df_features['derivative'] = df_features['magnitud'].diff().abs()
        else:
            df_features['mag_rolling_mean'] = df_features['magnitud']
            df_features['mag_rolling_std'] = 0
            df_features['derivative'] = 0
        
        # Seleccionar características (ordenadas por importancia)
        feature_columns = ['magnitud', 'mag_rolling_mean', 'mag_rolling_std', 
                          'derivative', 'accel_x', 'accel_y', 'accel_z']
        
        # Filtrar columnas que existen
        available_features = [col for col in feature_columns if col in df_features.columns]
        df_features = df_features[available_features].fillna(0)
        
        return df_features, available_features
    
    def generate_labels(self, df):
        """Genera etiquetas basadas en umbrales de magnitud"""
        df_labeled = df.copy()
        
        # Calcular magnitud si no existe
        if 'magnitud' not in df_labeled.columns:
            df_labeled['magnitud'] = np.sqrt(
                df_labeled['accel_x']**2 + 
                df_labeled['accel_y']**2 + 
                df_labeled['accel_z']**2
            )
        
        # Asignar etiquetas según umbrales
        condiciones = [
            df_labeled['magnitud'] <= THRESHOLD_NORMAL,
            (df_labeled['magnitud'] > THRESHOLD_NORMAL) & (df_labeled['magnitud'] <= THRESHOLD_WARNING),
            df_labeled['magnitud'] > THRESHOLD_WARNING
        ]
        
        estados = ['normal', 'warning', 'failure']
        df_labeled['estado'] = np.select(condiciones, estados, default='normal')
        
        print("📊 Distribución de etiquetas generadas:")
        print(df_labeled['estado'].value_counts())
        
        return df_labeled
    
    def train(self, csv_file=None, df=None):
        """Entrena el modelo KNN"""
        print("\n" + "="*50)
        print("🔄 ENTRENANDO MODELO KNN")
        print("="*50)
        
        # Cargar datos
        if df is None and csv_file:
            df = pd.read_csv(csv_file)
        elif df is None:
            if not os.path.exists(CSV_FILE):
                print(f"❌ Archivo no encontrado: {CSV_FILE}")
                return False
            df = pd.read_csv(CSV_FILE)
        
        if len(df) == 0:
            print("❌ No hay datos para entrenar")
            return False
        
        print(f"📊 Datos cargados: {len(df)} registros")
        
        # Verificar si hay suficientes datos
        if len(df) < 20:
            print("⚠️ Pocos datos para entrenar. Se recomiendan al menos 20 registros")
        
        # Generar etiquetas si no existen
        if 'estado' not in df.columns or df['estado'].isna().all():
            print("⚠️ Generando etiquetas automáticas...")
            df = self.generate_labels(df)
        elif 'estado_real' in df.columns:
            # Usar estado_real si existe
            df['estado'] = df['estado_real']
        
        # Calcular características
        X, self.feature_names = self.calculate_features(df)
        y = df['estado'].values
        self.classes_ = np.unique(y)
        
        print(f"🔧 Características usadas: {self.feature_names}")
        print(f"📊 Matriz de características: {X.shape}")
        print(f"🏷️ Clases: {self.classes_}")
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
        
        print(f"📂 División: {len(X_train)} entrenamiento, {len(X_test)} prueba")
        
        # Normalizar
        X_train_norm = self.scaler.fit_transform(X_train)
        X_test_norm = self.scaler.transform(X_test)
        
        # Entrenar
        self.model.fit(X_train_norm, y_train)
        
        # Evaluar
        y_pred = self.model.predict(X_test_norm)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n📈 Precisión del modelo: {accuracy:.2%}")
        print("\n📋 Reporte de clasificación:")
        print(classification_report(y_test, y_pred))
        
        print("\n🔢 Matriz de confusión:")
        print(confusion_matrix(y_test, y_pred))
        
        self.is_trained = True
        
        # Guardar modelo y métricas
        self.save_model()
        self.save_metrics(accuracy, y_test, y_pred)
        
        return True
    
    def predict(self, data):
        """Predice el estado de una lectura individual"""
        if not self.is_trained:
            print("⚠️ Modelo no entrenado")
            return None
        
        # Convertir a DataFrame
        df = pd.DataFrame([data])
        X, _ = self.calculate_features(df)
        X_norm = self.scaler.transform(X)
        
        # Predecir
        prediction = self.model.predict(X_norm)[0]
        probabilities = self.model.predict_proba(X_norm)[0]
        confidence = max(probabilities)
        
        return {
            'estado': prediction,
            'confianza': confidence,
            'probabilidades': dict(zip(self.classes_, probabilities))
        }
    
    def save_model(self):
        """Guarda el modelo entrenado"""
        os.makedirs(MODELS_DIR, exist_ok=True)
        model_path = os.path.join(MODELS_DIR, 'knn_model.pkl')
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'classes_': self.classes_
        }
        joblib.dump(model_data, model_path)
        print(f"💾 Modelo guardado en: {model_path}")
    
    def load_model(self):
        """Carga un modelo previamente entrenado"""
        model_path = os.path.join(MODELS_DIR, 'knn_model.pkl')
        
        try:
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.classes_ = model_data['classes_']
            self.is_trained = True
            print(f"✅ Modelo cargado desde: {model_path}")
            print(f"   Clases: {self.classes_}")
            return True
        except FileNotFoundError:
            print(f"⚠️ No se encontró modelo en: {model_path}")
            return False
        except Exception as e:
            print(f"⚠️ Error cargando modelo: {e}")
            return False
    
    def save_metrics(self, accuracy, y_test, y_pred):
        """Guarda las métricas del modelo"""
        os.makedirs(MODELS_DIR, exist_ok=True)
        metrics_path = os.path.join(MODELS_DIR, 'metrics.json')
        
        metrics = {
            'accuracy': float(accuracy),
            'classes': list(self.classes_),
            'features': self.feature_names,
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'n_neighbors': KNN_NEIGHBORS,
            'weights': KNN_WEIGHTS
        }
        
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"💾 Métricas guardadas en: {metrics_path}")


# Prueba rápida
if __name__ == "__main__":
    print("Probando KNN Predictor...")
    predictor = KNNPredictor()
    
    # Crear datos de prueba
    test_data = pd.DataFrame({
        'accel_x': [0.1, 1.5, 3.0],
        'accel_y': [0.0, 1.2, 2.5],
        'accel_z': [9.8, 11.5, 14.0]
    })
    
    # Entrenar con datos simulados
    print("\nCreando datos sintéticos para entrenamiento...")
    np.random.seed(42)
    synthetic_data = pd.DataFrame({
        'accel_x': np.random.normal(0, 0.5, 100),
        'accel_y': np.random.normal(0, 0.5, 100),
        'accel_z': np.random.normal(9.8, 0.3, 100),
        'estado': 'normal'
    })
    
    predictor.train(df=synthetic_data)
    
    print("\n🧪 Probando predicciones:")
    for i, row in test_data.iterrows():
        result = predictor.predict(row.to_dict())
        print(f"  {result}")