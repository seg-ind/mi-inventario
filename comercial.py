import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO PROFESIONAL
st.set_page_config(page_title="Gestión Comercial", layout="wide", page_icon="📈")

# Aplicamos los tonos azul oscuro y gris claro vía CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; } /* Gris muy claro de fondo */
    .stButton>button { 
        background-color: #002b5e; 
        color: white; 
        border-radius: 4px; 
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #004080;
        color: #e0e0e0;
    }
    h1, h2, h3 { color: #002b5e; }
    </style>
    """, unsafe_allow_html=True)


import streamlit as st
import os # Necesitamos esto para buscar el archivo

# 1. ESTILO Y CONFIGURACIÓN (Dejalo como estaba)
st.set_page_config(page_title="Gestión Comercial", layout="wide", page_icon="📈")

# 2. LOGO Y TÍTULO (Usando ruta local)
# Buscamos el archivo LOGO.jpg en la misma carpeta que el script
ruta_logo = os.path.join(os.path.dirname(__file__), 'LOGO.jpg')

# Verificamos si el archivo existe antes de mostrarlo
if os.path.exists(ruta_logo):
    col_l, col_r = st.columns([1, 4]) # 1 parte para logo, 4 para título
    with col_l:
        st.image(ruta_logo, width=150) # Mostramos el logo localmente
    with col_r:
        st.markdown("<h1 style='color: #002b5e;'>Gestión Comercial</h1>", unsafe_allow_html=True)
else:
    # Si por alguna razón no lo encuentra, mostramos solo el título
    st.title("Gestión Comercial")
    st.warning("⚠️ No se encontró el archivo 'LOGO.jpg' en GitHub.")





# 3. CONEXIÓN A DATOS (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)
URL_HOJA = "https://docs.google.com/spreadsheets/d/16yNdj9OJZuTlnKya1wbtTRV_Px7NNjNR0qEr7ePPax4/edit"

@st.cache_data(ttl=60) # Cache para que no recargue de Google cada segundo
def cargar_base_clientes():
    try:
        # Leemos la hoja (Asegurate que la pestaña se llame Clientes o sea la primera)
        df = conn.read(spreadsheet=URL_HOJA)
        df.columns = df.columns.str.strip()
        
        # Combinamos Cliente y Ubicación para el buscador
        if 'Cliente' in df.columns and 'Ubicacion' in df.columns:
            df['IDENTIFICACION'] = df['Cliente'].astype(str) + " - " + df['Ubicacion'].astype(str)
        else:
            st.error("Revisá las columnas de tu Excel: debe tener 'Cliente' y 'Ubicacion'")
            
        return df
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return pd.DataFrame(columns=['ID', 'Cliente', 'Ubicacion', 'IDENTIFICACION'])

df_clientes = cargar_base_clientes()

# 4. BUSCADORES (Pantalla de Inicio)
st.markdown("---")
st.subheader("🔍 Buscador de Clientes")
c_id, c_ident = st.columns(2)

with c_id:
    busqueda_id = st.text_input("Código del Cliente (ID):")
with c_ident:
    busqueda_txt = st.text_input("Identificación (Nombre o Ubicación):")

# 5. FILTRADO DINÁMICO
df_filtrado = df_clientes.copy()

if busqueda_id:
    df_filtrado = df_filtrado[df_filtrado['ID'].astype(str).str.contains(busqueda_id, case=False, na=False)]

if busqueda_txt:
    df_filtrado = df_filtrado[df_filtrado['IDENTIFICACION'].str.contains(busqueda_txt, case=False, na=False)]

# 6. TABLA DE RESULTADOS CON BOTONES
st.write("### Resultados")

# Encabezados
h_id, h_ident, h_btns = st.columns([1, 4, 5])
h_id.write("**ID**")
h_ident.write("**IDENTIFICACIÓN (CLIENTE - UBICACIÓN)**")
h_btns.write("**ACCIONES**")

if not df_filtrado.empty:
    for i, fila in df_filtrado.iterrows():
        r_id, r_ident, r_btns = st.columns([1, 4, 5])
        
        r_id.write(fila['ID'])
        r_ident.write(fila['IDENTIFICACION'])
        
        # Generación de los 6 botones por cada fila
        with r_btns:
            b1, b2, b3, b4, b5, b6 = st.columns(6)
            # Definiremos la funcionalidad de estos botones en las siguientes etapas
            b1.button("📄", key=f"pres_{i}", help="Presupuestos")
            b2.button("🛠️", key=f"ot_{i}", help="Orden de Trabajo")
            b3.button("🚚", key=f"seg_{i}", help="Seguimiento")
            b4.button("💰", key=f"cob_{i}", help="Facturación/Cobranzas")
            b5.button("📊", key=f"rep_{i}", help="Reportes")
            b6.button("✉️", key=f"mail_{i}", help="Enviar Mail")
else:
    st.info("No hay coincidencias para mostrar.")











