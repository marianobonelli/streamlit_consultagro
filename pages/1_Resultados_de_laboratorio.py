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

st.session_state.page2_completed = False
#st.title('Consultagro')
# Cargar la imagen
imagen = Image.open("logo.png")
# Mostrar la imagen en la aplicación
st.image(imagen, use_column_width=False)

if st.session_state.control_de_flujo == True: # Access the value from session state
    
    # Busca el primer archivo .xlsx entre los subidos
    st.session_state.xlsx_files = [file for file in st.session_state.uploaded_files if file.name.endswith('.xlsx')]
    if len(st.session_state.xlsx_files) > 0:            
        # Lee el primer archivo .xlsx subido como un dataframe
        st.session_state.uploaded_file = st.session_state.xlsx_files[0]
        st.session_state.df = pd.read_excel(st.session_state.uploaded_file, skiprows=3)

        def round_if_numeric(x):
                if pd.api.types.is_numeric_dtype(x):
                    return round(x, 3)
                else:
                    return x
                
        st.session_state.df = st.session_state.df.apply(round_if_numeric)
        columns = [col.replace(' ', '').replace('.', '') for col in st.session_state.df.columns]
        st.session_state.df = st.session_state.df.rename(columns=dict(zip(st.session_state.df.columns, columns)))

        if is_datetime(st.session_state.df["Fecha"]):
                st.session_state.df["Fecha"] = st.session_state.df["Fecha"].dt.strftime("%Y-%m-%d")


        st.write('Resultados de laboratorio:')
        #st.dataframe(st.session_state.df.transpose()) # df rotado df.transpose()

        st.dataframe(st.session_state.df.transpose(), height=500)

        ###
        st.session_state.page2_completed = True

        st.caption("Bv. Belgrano 453, Rufino, Santa Fe")
        st.caption("www.consultagroest.com.ar")
        st.caption("WhatsApp: 3382574215")


else:
     st.warning("Debe cargar al menos un archivo excel y un csv para continuar")