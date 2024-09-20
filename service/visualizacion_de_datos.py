import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator
from dotenv import load_dotenv
import os

load_dotenv()
PATH_IMAGES = os.getenv("PATH_IMAGES")


def generar_grafico_torta(tiempo_prendido, tiempo_apagado, tiempo_pausado, tiempo_en_ejecucion, tiempo_detectando, tiempo_sin_detectar, tiempo_microsueno, tiempo_distraccion):
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    # Titulos de todos los gráficos
    fig.suptitle('Gráficos de Torta', fontweight='bold', fontsize=14)

    # Gráfico de torta 1
    labels = ['Tiempo prendido', 'Tiempo apagado']
    values = [tiempo_prendido, tiempo_apagado]
    colors = ['#FF6F00', '#1E88E5']
    axs[0, 0].pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white'})
    axs[0, 0].axis('equal')
    axs[0, 0].set_title('Distribución de tiempos en los que la app estaba prendida')

    # Gráfico de torta 2
    labels = ['Tiempo pausado', 'Tiempo en ejecución']
    values = [tiempo_pausado, tiempo_en_ejecucion]
    colors = ['#FF4081', '#42A5F5']
    axs[0, 1].pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white'})
    axs[0, 1].axis('equal')
    axs[0, 1].set_title('Distribución de tiempos en los que la app estaba pausada')

    # Gráfico de torta 3
    labels = ['Tiempo detectando', 'Tiempo sin detectar']
    values = [tiempo_detectando, tiempo_sin_detectar]
    colors = ['#FF5252', '#448AFF']
    axs[1, 0].pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white'})
    axs[1, 0].axis('equal')
    axs[1, 0].set_title('Distribución de tiempos en los que la app estaba detectando')

    # Gráfico de torta 4
    labels = ['Tiempo microsueño', 'Tiempo de distracción']
    values = [tiempo_microsueno, tiempo_distraccion]
    colors = ['#FF5722', '#FFC107']
    axs[1, 1].pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white'})
    axs[1, 1].axis('equal')
    axs[1, 1].set_title('Distribución de tiempos en los que sonaba la alarma')

    # Ajustar el espacio entre los gráficos
    plt.tight_layout()
    return fig

def generar_diagrama_de_barras_de_frecuencias_agrupadas_por_recorrido(df):

    recorridos = df['recorrido'].unique()
    causas = ['microsueño', 'distraccion', 'pause']

    frecuencias = []
    for recorrido in recorridos:
        filtro_recorrido = df['recorrido'] == recorrido
        frecuencias_recorrido = []
        for causa in causas:
            filtro_causa = df['causa'] == causa
            frecuencia = df[filtro_recorrido & filtro_causa].shape[0]
            frecuencias_recorrido.append(frecuencia)
        frecuencias.append(frecuencias_recorrido)

    x = recorridos
    y = zip(*frecuencias)
    etiquetas = ['Microsueño', 'Distracción', 'Pausa']

    fig, ax = plt.subplots()
    ax.bar(x - 0.2, next(y), width=0.2, label=etiquetas[0])
    ax.bar(x, next(y), width=0.2, label=etiquetas[1])
    ax.bar(x + 0.2, next(y), width=0.2, label=etiquetas[2])

    ax.set_xlabel('Recorrido')
    ax.set_ylabel('Cantidad de Registros')
    ax.set_title('Frecuencias por Recorrido', fontweight='bold', fontsize=14)
    ax.set_xticks(recorridos)
    ax.legend()
    return fig


# Función para generar el diagrama de frecuencias
def generar_diagrama_de_areas_de_frecuencias_por_hora(df):
    df['hora'] = pd.to_datetime(df['hora'], format='%H:%M')
    microsuenos = df[df['causa'] == 'microsueño'].copy()
    distracciones = df[df['causa'] == 'distraccion'].copy()
    pausas = df[df['causa'] == 'pause'].copy()

    # Asignar valores a la columna "fecha" utilizando loc
    microsuenos.loc[:, 'fecha'] = microsuenos['hora']
    distracciones.loc[:, 'fecha'] = distracciones['hora']
    pausas.loc[:, 'fecha'] = pausas['hora']

    # Calcular la frecuencia por hora
    frecuencia_microsuenos = microsuenos.resample('H', on='fecha').size().fillna(0)
    frecuencia_distracciones = distracciones.resample('H', on='fecha').size().fillna(0)
    frecuencia_pausas = pausas.resample('H', on='fecha').size().fillna(0)

    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Generar el gráfico
    ax.fill_between(frecuencia_microsuenos.index, frecuencia_microsuenos, alpha=0.5, label='Microsueños')
    ax.fill_between(frecuencia_distracciones.index, frecuencia_distracciones, alpha=0.5, label='Distracciones')
    ax.fill_between(frecuencia_pausas.index, frecuencia_pausas, alpha=0.5, label='Pausas')


    # Configurar el eje x
    ax.xaxis.set_major_locator(HourLocator(interval=1))
    ax.xaxis.set_major_formatter(DateFormatter('%H'))
    ax.set_xlabel('Hora')
    ax.set_ylabel('Cantidad de Registros')
    ax.set_title('Frecuencias por Hora', fontweight='bold', fontsize=14)
    ax.legend()
    return fig

def guardar_en_cache(graficos):
    # Guardar los gráficos en la caché
    for i, grafico in enumerate(graficos):
        grafico.savefig(f"{PATH_IMAGES}grafico{i}.png")
    # devuelve una lista de las rutas de los archivos
    return [f"{PATH_IMAGES}grafico{i}.png" for i in range(len(graficos))]
