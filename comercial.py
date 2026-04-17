#URL_HOJA = "https://docs.google.com/spreadsheets/d/16yNdj9OJZuTlnKya1wbtTRV_Px7NNjNR0qEr7ePPax4/edit?usp=sharing"





import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gestión Comercial", layout="wide")

# Estilo personalizado (Azul oscuro y Gris)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #002b5e; color: white; border-radius: 5px; width: 100%; }
    h1, h2, h3 { color: #002b5e; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGO (Búsqueda flexible en el repositorio)
col_l, col_r = st.columns([1, 4])
with col_l:
    # Intentamos encontrar el logo sin importar si es .jpg, .JPG o .png
    archivo_logo = None
    for nombre in ['LOGO.jpg', 'logo.jpg', 'LOGO.JPG', 'LOGO.png', 'logo.png']:
        ruta_posible = os.path.join(os.path.dirname(__file__), nombre)
        if os.path.exists(ruta_posible):
            archivo_logo = ruta_posible
            break
    
    if archivo_logo:
        st.image(archivo_logo, width=150)
    else:
        st.info("Logo no detectado")

with col_r:
    st.title("Gestión Comercial")

# 3. CONEXIÓN A GOOGLE SHEETS
# REEMPLAZA ESTA URL POR LA TUYA REAL
URL_HOJA = "https://docs.google.com/spreadsheets/d/16yNdj9OJZuTlnKya1wbtTRV_Px7NNjNR0qEr7ePPax4/edit"

conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # Leemos los datos de la primera pestaña
        df = conn.read(spreadsheet=URL_HOJA)
        
        # Limpieza estándar de columnas (quita espacios y tildes comunes)
        df.columns = [str(c).strip().upper().replace('Ó', 'O').replace('Á', 'A') for c in df.columns]
        
        # Renombrado seguro para el sistema
        mapeo = {'ID': 'ID', 'CLIENTE': 'Cliente', 'UBICACION': 'Ubicacion'}
        df = df.rename(columns=mapeo)
        
        # Crear columna combinada para búsqueda rápida
        if 'Cliente' in df.columns and 'Ubicacion' in df.columns:
            df['IDENTIFICACION'] = df['Cliente'].astype(str) + " - " + df['Ubicacion'].astype(str)
        
        return df
    except Exception as e:
        # Si falla, devolvemos None para manejarlo en la interfaz
        return None

df_clientes = cargar_datos()

# 4. INTERFAZ DE BUSQUEDA
st.markdown("---")
col_bus1, col_bus2 = st.columns(2)

with col_bus1:
    bus_id = st.text_input("Código del Cliente (ID):")
with col_bus2:
    bus_txt = st.text_input("Identificación (Nombre o Ubicación):")

# 5. RESULTADOS
if df_clientes is not None:
    # Aplicar filtros
    df_f = df_clientes.copy()
    if bus_id:
        df_f = df_f[df_f['ID'].astype(str).str.contains(bus_id, case=False, na=False)]
    if bus_txt:
        df_f = df_f[df_f['IDENTIFICACION'].str.contains(bus_txt, case=False, na=False)]

    # Mostrar Tabla
    st.subheader("Resultados")
    
    # Encabezados de la tabla
    h1, h2, h3 = st.columns([1, 3, 4])
    h1.write("**ID**")
    h2.write("**IDENTIFICACIÓN**")
    h3.write("**ACCIONES**")

    if not df_f.empty:
        for i, fila in df_f.iterrows():
            r1, r2, r3 = st.columns([1, 3, 4])
            r1.write(str(fila['ID']))
            r2.write(fila['IDENTIFICACION'])
            
            with r3:
                btn_cols = st.columns(6)
                btn_cols[0].button("📄", key=f"p_{i}", help="Presupuesto")
                btn_cols[1].button("🛠️", key=f"o_{i}", help="OT")
                btn_cols[2].button("🚚", key=f"s_{i}", help="Seguimiento")
                btn_cols[3].button("💰", key=f"c_{i}", help="Cobranza")
                btn_cols[4].button("📊", key=f"r_{i}", help="Reporte")
                btn_cols[5].button("✉️", key=f"m_{i}", help="Mail")
    else:
        st.info("No se encontraron coincidencias.")

else:
    # Mensaje amigable si la conexión falla
    st.error("❌ No se pudo conectar con Google Sheets.")
    st.markdown("""
    **Pasos para solucionar:**
    1. Revisa que pegaste los **Secrets** en esta App nueva.
    2. Asegúrate de que el **link de la hoja** sea correcto en el código.
    3. Dale permiso de **Editor** al email del bot en el botón 'Compartir' de tu Excel.
    """)