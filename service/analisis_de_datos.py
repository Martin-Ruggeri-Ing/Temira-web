import pandas as pd
import streamlit as st
from datetime import datetime, timedelta


# Cargar el archivo CSV
@st.cache_data
def cargar_datos(archivo_csv):
    converters = {'inicio': convertir_fecha, 'fin': convertir_fecha}
    df = pd.read_csv(archivo_csv, converters=converters)
    # Verificar que todos los campos estén escritos correctamente
    df['causa'] = df['causa'].apply(lambda x: x.lower())
    df = df[df['causa'].isin(['microsueño', 'distraccion','on', 'off', 'pause', 'play'])]
    # Eliminar registros con irregularidades en cualquier campo o columna
    df = df.dropna()
    # Combinar registros de pausa y play
    df = combinar_registros(df)
    # Agregar duración de la alarma
    df = agregar_duracion(df)
    return df

def combinar_registros(df):
    nuevos_registros = []
    i = 0
    while i < len(df):
        if df['causa'][i] == 'pause' and i + 1 < len(df) and df['causa'][i + 1] == 'play':
            inicio_pause = df['inicio'][i]
            fin_play = df['fin'][i + 1]
            nuevos_registros.append([inicio_pause, fin_play, 'pause'])
            i += 2
        else:
            nuevos_registros.append([df['inicio'][i], df['fin'][i], df['causa'][i]])
            i += 1
    nuevo_df = pd.DataFrame(nuevos_registros, columns=['inicio', 'fin', 'causa'])
    return nuevo_df

def calcular_tiempo_total(df):
    # Obtener la fecha del primer "on" y último "off"
    primer_registro = df[df['causa'] == 'on']['inicio'].iloc[0]
    ultimo_registro = df[df['causa'] == 'off']['fin'].iloc[-1]

    # Calcular el tiempo total en segundos
    tiempo_total = (ultimo_registro - primer_registro).total_seconds()
    return tiempo_total

def calcular_tiempos_prendido_y_apagado(df, tiempo_total):
    # Filtrar los registros de encendido (on) y apagado (off)
    encendido = df[df['causa'] == 'on']
    apagado = df[df['causa'] == 'off']
    # Calcular el tiempo prendido como la suma de los tiempos entre fin on y fin off
    tiempo_prendido = 0
    for i in range(len(encendido)):
        tiempo_prendido += (apagado['fin'].iloc[i] - encendido['fin'].iloc[i]).total_seconds()
    # Calcular el tiempo apagado como el tiempo total menos el tiempo prendido
    tiempo_apagado = tiempo_total - tiempo_prendido

    return tiempo_prendido, tiempo_apagado

def calcular_tiempos_pausado_y_en_ejecucion(df, tiempo_prendido):
    # calcular tiempo pausado como la suma de las duraciones de los registros pause
    tiempo_pausado = df[df['causa'] == 'pause']['duracion'].sum()
    tiempo_en_ejecucion = tiempo_prendido - tiempo_pausado
    return tiempo_pausado, tiempo_en_ejecucion

def calcular_tiempos_detectando_somnolencia_y_sin_detectar(df, tiempo_en_ejecucion):
    tiempo_microsueno = df[df['causa'] == 'microsueño']['duracion'].sum()
    tiempo_distraccion = df[df['causa'] == 'distraccion']['duracion'].sum()
    tiempo_detectando_somnolencia = tiempo_microsueno + tiempo_distraccion
    tiempo_sin_detectar_somnolencia = tiempo_en_ejecucion - tiempo_detectando_somnolencia

    return tiempo_detectando_somnolencia, tiempo_sin_detectar_somnolencia, tiempo_microsueno, tiempo_distraccion

# Función para convertir la fecha con manejo de excepciones
def convertir_fecha(x):
    try:
        return datetime.strptime(x, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        return pd.NaT

def agregar_duracion(df):
    df['inicio'] = pd.to_datetime(df['inicio'])
    df['fin'] = pd.to_datetime(df['fin'])
    df['duracion'] = (df['fin'] - df['inicio']).dt.total_seconds()
    return df

def calcular_frecuencia_por_hora_independiente_del_dia(df):
    # Filtrar los datos de pausas, microsueños y distracciones
    microsuenos = df[df['causa'] == 'microsueño'].copy()
    distracciones = df[df['causa'] == 'distraccion'].copy()
    # pausas = df[df['causa'] == 'pause']

    # Convertir la columna "hora" en un objeto DateTime y extraer solo las horas
    microsuenos['hora'] = pd.to_datetime(microsuenos['inicio']).dt.time
    distracciones['hora'] = pd.to_datetime(distracciones['inicio']).dt.time

    # Establecer la columna "hora" como índice
    microsuenos.set_index('hora', inplace=True)
    distracciones.set_index('hora', inplace=True)

    # Convertir el índice en un DateTimeIndex
    microsuenos.index = pd.to_datetime(microsuenos.index)
    distracciones.index = pd.to_datetime(distracciones.index)

    # Calcular la frecuencia por hora de microsueños
    frecuencia_microsuenos = microsuenos.resample('H').size().fillna(0)
    frecuencia_distracciones = distracciones.resample('H').size().fillna(0)


    print(frecuencia_microsuenos)
    print(frecuencia_distracciones)
    return frecuencia_microsuenos, frecuencia_distracciones

def agregar_horas(df):
    # Convertir la columna "hora" en un objeto DateTime y extraer solo las horas
    df['hora'] = pd.to_datetime(df['inicio']).dt.time
    # Establecer formato
    df['hora'] = df['hora'].apply(lambda x: x.strftime('%H:%M'))
    return df

def agregar_recorrido(df):
    recorrido = 0
    recorridos = []
    on_count = 0
    off_count = 0

    for index, row in df.iterrows():
        if row['causa'] == 'on':
            on_count += 1
            recorrido = on_count
        elif row['causa'] == 'off':
            off_count += 1
            recorrido = off_count
        recorridos.append(recorrido)

    df['recorrido'] = recorridos
    return df