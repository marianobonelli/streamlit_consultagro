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

# Cargar la imagen
page_icon = Image.open("Logo2.png")

st.set_page_config(
    page_title="Consultagro",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "Desarrollado por Mariano Bonelli para Consultagro. Para mas información comunicarse al email: mbonelli95@gmail.com"
    }
)

# Cargar la imagen
imagen = Image.open("logo.png")
# Mostrar la imagen en la aplicación
st.image(imagen, use_column_width=False)




st.session_state.uploaded_files = st.file_uploader(
    "Selecciona el archivo excel con los resultados de laboratorio y los archivos csv con las coordenadas del calador",
    type=['csv', 'xlsx'],
    accept_multiple_files=True)

csv_uploaded = False
xlsx_uploaded = False
st.session_state.control_de_flujo = False

for uploaded_file in st.session_state.uploaded_files:
    if uploaded_file.type == 'text/csv':
        csv_uploaded = True
    elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        xlsx_uploaded = True

if csv_uploaded and xlsx_uploaded:
        control_de_flujo = True
        st.session_state.control_de_flujo = True # Store the value in session state
else:
     st.warning("Debe cargar al menos un archivo excel y un csv para continuar")


st.caption("Bv. Belgrano 453, Rufino, Santa Fe")
st.caption("www.consultagroest.com.ar")
st.caption("WhatsApp: 3382574215")


   
