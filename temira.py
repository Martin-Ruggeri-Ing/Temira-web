import base64
import tempfile
import streamlit as st
from service.analisis_de_datos import agregar_horas, calcular_tiempos_detectando_somnolencia_y_sin_detectar, calcular_tiempos_pausado_y_en_ejecucion, calcular_tiempos_prendido_y_apagado, cargar_datos, calcular_tiempo_total, agregar_recorrido
from service.visualizacion_de_datos import generar_diagrama_de_areas_de_frecuencias_por_hora, generar_diagrama_de_barras_de_frecuencias_agrupadas_por_recorrido, generar_grafico_torta
from service.encriptacion import leer_clave
from service.encriptacion import desencriptar_archivo
from dotenv import load_dotenv
import os

load_dotenv()
PATH_LOGO = os.getenv("PATH_LOGO")
PATH_FONDO = os.getenv("PATH_FONDO")


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

# Carga del archivo y ejecución de la app
def main():
    logo = PATH_LOGO
    fondo = PATH_FONDO
    clave_privada = leer_clave('privada')
    st.set_page_config(page_title='Temira', page_icon=logo)
    st.title("TEMIRA")
    st.image(logo, width=300)
    add_bg_from_local(fondo)
    st.markdown('# Análisis de Deteciones de Microsueños y Distracciones')
    st.markdown('### Esta aplicación permite analizar los datos de las detecciones de microsueños y distracciones realizadas por la aplicación Temira. Para ello, se debe cargar un archivo CSV con los datos de las detecciones.')
    # Boton de ayuda que despliega un texto con instrucciones para cargar el csv
    if st.button('Ayuda'):
        st.markdown('Para cargar el archivo, se debe hacer click en el botón "Cargar archivo CSV" y seleccionar el archivo correspondiente. El archivo debe tener el siguiente formato:')

    archivo_encriptado = st.file_uploader('Cargar archivo encriptado', type=['csv'])

    if archivo_encriptado is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(archivo_encriptado.read())
            ruta_temporal = temp_file.name

        contenido_desencriptado = desencriptar_archivo(clave_privada, ruta_temporal)
        # Crear un archivo temporal para cargar los datos desencriptados
        with tempfile.NamedTemporaryFile(delete=False) as archivo_temporal:
            archivo_temporal.write(contenido_desencriptado)

        datos = cargar_datos(archivo_temporal.name)
        # Mostrar la tabla de datos
        st.subheader("Datos del archivo CSV")
        st.dataframe(datos)

        # Mostrar el gráfico de torta
        st.subheader("Gráfico de Torta")
        st.markdown('Este gráfico muestra la distribución de tiempos en los que la app estaba prendida y en los que sonaba la alarma')
        tiempo_total = calcular_tiempo_total(datos)
        tiempo_prendido, tiempo_apagado = calcular_tiempos_prendido_y_apagado(datos, tiempo_total)
        tiempo_pausado, tiempo_en_ejecucion = calcular_tiempos_pausado_y_en_ejecucion(datos, tiempo_prendido)
        tiempo_detectando, tiempo_sin_detectar, tiempo_microsueno, tiempo_distraccion = calcular_tiempos_detectando_somnolencia_y_sin_detectar(datos, tiempo_en_ejecucion)
        fig1 = generar_grafico_torta(tiempo_prendido, tiempo_apagado, tiempo_pausado, tiempo_en_ejecucion, tiempo_detectando, tiempo_sin_detectar, tiempo_microsueno, tiempo_distraccion)
        st.pyplot(fig1)

        # Mostrar el diagrama de frecuencias por recorrido
        st.subheader("Diagrama de Frecuencias por Recorrido")
        st.markdown('Este diagrama muestra la cantidad de pausas, microsueños y distracciones por recorrido')
        datos = agregar_recorrido(datos)
        st.subheader("Dataframe con recorridos")
        st.dataframe(datos)
        fig2 = generar_diagrama_de_barras_de_frecuencias_agrupadas_por_recorrido(datos)
        st.pyplot(fig2)

        # Mostrar el diagramas de frecuencias
        st.subheader("Diagramas de Frecuencias Horarias")
        st.markdown('Este diagrama muestra la cantidad de detecciones de microsueños y distracciones por hora')
        datos1 = agregar_horas(datos)
        st.subheader("Dataframe con horas")
        st.dataframe(datos1)

        fig3 = generar_diagrama_de_areas_de_frecuencias_por_hora(datos1)
        st.pyplot(fig3)

        # Botón para generar el informe PDF
        st.title("Generar Informe PDF")
        # codigo para que mientras no ingrese el nombre del conductor no se mostrara el boton de descarga
        with st.form("NombreConductorForm"):
            nombre_conductor = ""
            nombre_conductor = st.text_input("Ingrese el nombre del conductor")
            submit_button = st.form_submit_button("OK")
    
        if submit_button and nombre_conductor:
            # Generar el informe PDF
            graficos = [fig1, fig2, fig3]
            nombre_informe = "informe de " + nombre_conductor
            archivos_cachados = guardar_en_cache(graficos)
            informe_pdf = generar_informe_pdf(archivos_cachados, nombre_conductor)
            # Descargar el archivo PDF utilizando el botón de descarga de Streamlit
            st.download_button(
                label="Descargar Informe PDF",
                data=informe_pdf,
                file_name=f"{nombre_informe}.pdf",
                mime="application/pdf"
            )


# Ejecutar la app
if __name__ == '__main__':
    main()
