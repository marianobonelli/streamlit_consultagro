import base64
import fiona
import folium
import geopandas as gpd
import io
import os
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from PIL import Image
import re
from shapely.geometry import Point
from shapely.ops import unary_union
import shutil
import streamlit as st
from streamlit_folium import folium_static
import tempfile
st.session_state.page3_completed = False
# Cargar la imagen
imagen = Image.open("logo.png")
# Mostrar la imagen en la aplicación
st.image(imagen, use_column_width=False)


if st.session_state.control_de_flujo == True: # Access the value from session state
    if st.session_state.page2_completed == True:

        # Suponiendo que el DataFrame df ya está creado
        # Limpiamos las columnas "Profundidad" 
        st.session_state.df['Lote'] = st.session_state.df['Lote'].str.strip()

        # 1. Detectar cuántos valores únicos hay en la columna "Lote" del dataframe df
        valores_unicos = st.session_state.df['Lote'].unique()

        # 2. Generar un selectbox para cada valor único y listar archivos CSV en /content/
        csv_files = [file.name for file in st.session_state.uploaded_files if file.name.endswith('.csv')]

        # Crear un diccionario para almacenar los selectbox y los valores seleccionados
        st.session_state.selectboxes = {}

        for valor in valores_unicos:
            selectbox = st.selectbox(f'Lote {valor}:', csv_files, key=f'selectbox_{valor}')
            st.session_state.selectboxes[valor] = selectbox
        
        st.session_state.page3_completed = True

        st.caption("Bv. Belgrano 453, Rufino, Santa Fe")
        st.caption("www.consultagroest.com.ar")
        st.caption("WhatsApp: 3382574215")

    else:
     st.warning("Debe ir primero a Resultados de laboratorio")

else:
     st.warning("Debe cargar al menos un archivo excel y un csv para continuar")