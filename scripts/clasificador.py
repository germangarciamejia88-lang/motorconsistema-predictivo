import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# 1. Cargar el archivo CSV
# Cambia 'datos_esp32.csv' por el nombre real de tu archivo
# Asegúrate de que los nombres de las columnas coincidan ('X', 'Y', 'Z')
df = pd.read_csv('carga-g.csv')

# 2. Configurar el filtro Pasa Altas (Para eliminar la gravedad)
# Ajusta la frecuencia de muestreo (Fs) según los milisegundos de tu ESP32
Fs = 100.0  # Ejemplo: 100 Hz (si tomabas un dato cada 10ms)
Fc = 0.5    # Frecuencia de corte: elimina todo lo que cambie más lento que 0.5 Hz

def filtro_pasa_altas(data, cutoff, fs, order=2):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return filtfilt(b, a, data)

# Aplicar el filtro a cada eje
df['X_limpio'] = filtro_pasa_altas(df['X'], Fc, Fs)
df['Y_limpio'] = filtro_pasa_altas(df['Y'], Fc, Fs)
df['Z_limpio'] = filtro_pasa_altas(df['Z'], Fc, Fs)

# 3. Calcular la Magnitud Total de la Vibración (Vector)
df['Magnitud_Vibracion'] = np.sqrt(df['X_limpio']**2 + df['Y_limpio']**2 + df['Z_limpio']**2)

# 4. Calcular el valor global RMS de la vibración
rms_total = np.sqrt(np.mean(df['Magnitud_Vibracion']**2))
print(f"La vibración promedio (RMS) del ensayo es: {rms_total:.4f}")

# 5. Graficar los resultados
plt.figure(figsize=(12, 6))
plt.plot(df['Magnitud_Vibracion'], label='Magnitud de Vibración (Sin Gravedad)', color='purple')
plt.axhline(y=rms_total, color='r', linestyle='--', label=f'Valor RMS Global ({rms_total:.2f})')
plt.title('Análisis de Vibración - Datos ESP32')
plt.xlabel('Número de Muestra')
plt.ylabel('Aceleración')
plt.legend()
plt.grid(True)
plt.show()