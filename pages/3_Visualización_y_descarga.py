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
imagen = Image.open("logo.png")
# Mostrar la imagen en la aplicación
st.image(imagen, use_column_width=False)

if st.session_state.control_de_flujo == True: # Access the value from session state
    if st.session_state.page3_completed == True:
    

############
        def modify_csv_file(file):
            lines = file.readlines()
            
            # Decode lines from bytes to strings and add ; in the first row
            decoded_lines = [line.decode('utf-8') for line in lines]
            decoded_lines[0] = decoded_lines[0].rstrip() + ';\n'

            # Encode lines back to bytes and return the modified CSV content as a BytesIO object
            encoded_lines = [line.encode('utf-8') for line in decoded_lines]
            return io.BytesIO(b"".join(encoded_lines))


        def csv_to_geodataframe(file, name):
            # Leer el archivo CSV modificado
            df = pd.read_csv(file, delimiter=';', skipinitialspace=True)

            # Agregar una columna con el nombre del GeoDataFrame
            df['Lote'] = name

            # Convertir en un GeoDataFrame utilizando las columnas "Latitud" y "Longitud"
            geometry = [Point(xy) for xy in zip(df['Latitud'], df['Longitud'])]
            gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

            return gdf

        def get_selected_values(selectboxes):
            selected_values = {}
            for valor, selectbox_value in selectboxes.items():
                for uploaded_file in st.session_state.uploaded_files:
                    if uploaded_file.name == selectbox_value:
                        selected_values[valor] = uploaded_file
                        break
            return selected_values              
            
        selected_values = get_selected_values(st.session_state.selectboxes)

        if selected_values is None or '-Selecciona un valor-' in selected_values:
            st.warning("Al menos uno de los lotes no tiene un archivo CSV seleccionado")
        else:

            # Modificar y convertir cada archivo CSV en el diccionario
            st.session_state.geodataframes = {}

            for key, uploaded_file in selected_values.items():
                # Read the content of the uploaded file as bytes
                uploaded_file.seek(0)
                modified_file = modify_csv_file(uploaded_file)
                st.session_state.geodataframes[key] = csv_to_geodataframe(modified_file, key)

            # Ahora, el diccionario 'geodataframes' contiene GeoDataFrames en lugar de rutas a archivos CSV

            # Obtiene la primera clave del diccionario 'geodataframes'
            primer_key = next(iter(st.session_state.geodataframes))

            # Crea un mapa interactivo usando el primer GeoDataFrame del diccionario
            # y configurando las capas base y los atributos correspondientes
            # Lista de colores para asignar a cada GeoDataFrame
            colors = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow', 'black']

            # Calcula el centroide del mapa usando las coordenadas de todos los GeoDataFrames
            geoms = []
            for gdf in st.session_state.geodataframes.values():
                geoms.extend(gdf.geometry.tolist())
            centroid = unary_union(geoms).centroid.coords[0]
            st.session_state.center = [centroid[1], centroid[0]]  # intercambiar latitud y longitud
            st.session_state.zoom = 15

            # Crea el mapa con el centro y el zoom calculados
            m = folium.Map(location=st.session_state.center, zoom_start=st.session_state.zoom)

            color_index = 0

            # Itera sobre todas las claves en el diccionario 'geodataframes'
            for key in st.session_state.geodataframes.keys():
                # Añade el GeoDataFrame actual al mapa interactivo
                st.session_state.geodataframes[key].explore(
                    m=m,
                    tooltip=['Lote', 'Fecha', 'NRO', 'Modelo', 'Metodo', 'Profundidad 1', 'Profundidad 2', 'Latitud', 'Longitud'],
                    marker_kwds=dict(color=colors[color_index], radius=5),
                    name='Lote: ' + key,
                    show=False,
                )
                color_index += 1
                # Reinicia el índice de colores si alcanza el final de la lista de colores
                if color_index >= len(colors):
                    color_index = 0

        
        ############################################################################################################################################


            # Función para obtener el punto medio usando el índice medio (middle_row_index)
            def get_middle_geometry(geodf):
                middle_row_index = len(geodf) // 2
                return geodf.iloc[middle_row_index]["geometry"]

            # Función para agregar el valor del punto medio al dataframe df
            def add_middle_geometry_value(row, geodataframes):
                lote = row["Lote"]
                geodf = geodataframes.get(lote)
                if geodf is not None:
                    row["geometry"] = get_middle_geometry(geodf)
                return row

            # Aplicar la función add_middle_geometry_value a cada fila del dataframe df
            df = st.session_state.df.apply(add_middle_geometry_value, geodataframes=st.session_state.geodataframes, axis=1)

            # Transformar el DataFrame en un GeoDataFrame
            gdf = gpd.GeoDataFrame(df, geometry='geometry')

            # Asignar la proyección EPSG 4326 al GeoDataFrame
            gdf.crs = 'EPSG:4326'

            # Crear una carpeta para guardar los archivos shapefile
            output_folder = "export"
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # Corregimos el campo fecha
            
            if is_datetime(gdf["Fecha"]):
                gdf["Fecha"] = gdf["Fecha"].dt.strftime("%Y-%m-%d")

            # Eliminar espacios y puntos en los nombres de los campos
            columns = [col.replace(' ', '').replace('.', '') for col in gdf.columns]
            # Truncar los nombres de los campos a 10 caracteres
            columns = [col[:10] for col in columns]
            # Asignar los nuevos nombres de los campos al dataframe
            gdf = gdf.rename(columns=dict(zip(gdf.columns, columns)))

            def round_if_numeric(x):
                if pd.api.types.is_numeric_dtype(x):
                    return round(x, 3)
                else:
                    return x
                
            gdf = gdf.apply(round_if_numeric)

            # Agrupar el GeoDataFrame por las columnas "Lote" y "Profundidad"
            grouped_gdf = gdf.groupby(["Profundida"])

            fiona.drvsupport.supported_drivers['KML'] = 'rw'  # Habilitar el soporte de lectura y escritura para el formato KML

            def create_valid_layer_name(profundidad):
                valid_profundidad = re.sub(r"[^a-zA-Z0-9_]+", "", profundidad).replace(" ", "_")
                return f"{valid_profundidad}"

            #######   
            selector_primera_capa = True
            xlsx_name_from_uf = st.session_state.xlsx_files[0].name.replace('.xlsx', '')

            # Crear un directorio temporal para guardar los archivos shapefile y KML
            with tempfile.TemporaryDirectory() as output_folder:                  

                for (profundidad), group in grouped_gdf:

                    group.explore(
                        m=m,
                        marker_kwds=dict(color=colors[color_index], radius=5),
                        name=(f"{xlsx_name_from_uf}_{profundidad}").replace(' ', ''),
                        show=selector_primera_capa,
                        )
                    color_index += 1
                    selector_primera_capa = False
                    # Reinicia el índice de colores si alcanza el final de la lista de colores
                    if color_index >= len(colors):
                        color_index = 0

                    file_name_shp = (f"{xlsx_name_from_uf}_{profundidad}.shp").replace(' ', '')
                    file_name_kml = (f"{xlsx_name_from_uf}_{profundidad}.kml").replace(' ', '')
                    file_path_shp = os.path.join(output_folder, file_name_shp)
                    file_path_kml = os.path.join(output_folder, file_name_kml)

                    group.to_file(file_path_shp)
                    valid_layer_name = create_valid_layer_name(profundidad)
                    group.to_file(file_path_kml, driver='KML', layer=valid_layer_name)

                # Comprimir el directorio temporal
                zip_file_name = "export.zip"
                shutil.make_archive(zip_file_name.rstrip('.zip'), 'zip', output_folder)

            # Función para crear un enlace de descarga
            def create_download_link(file_path, file_name):
                with open(file_path, "rb") as f:
                    bytes = f.read()
                    b64 = base64.b64encode(bytes).decode()
                    href = f'<a href="data:file/zip;base64,{b64}" download="{file_name}">Descargar archivos</a>'
                    return href

            #Proporcionar un enlace de descarga en la aplicación Streamlit
            st.markdown(create_download_link(zip_file_name, "export.zip"), unsafe_allow_html=True)

            #######

            # Agrega la capa de teselas de Esri World Imagery
            tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}' 
            attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'

            # Agrega las capas de teselas adicionales y el control de capas
            folium.TileLayer(tiles, attr=attr, name='Esri World Imagery', show=True).add_to(m)
            folium.LayerControl(collapsed=False).add_to(m)

            folium_static(m)

            st.caption("Bv. Belgrano 453, Rufino, Santa Fe")
            st.caption("www.consultagroest.com.ar")
            st.caption("WhatsApp: 3382574215")
    else:
     st.warning("Debe ir primero a Selector Lote - CSV")
else:
     st.warning("Debe cargar al menos un archivo excel y un csv para continuar")