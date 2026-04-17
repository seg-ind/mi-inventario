import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="Gestión Comercial", layout="wide")

# 2. LOGO (Cambiamos a una imagen fija de prueba)
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png" # Ícono de empresa genérico
st.image(LOGO_URL, width=100)
st.title("Gestión Comercial")

# 3. VERIFICACIÓN DE SEGURIDAD (Esto te dirá el problema real)
if "connections" not in st.secrets:
    st.error("🚨 ERROR CRÍTICO: No se encontraron las credenciales en 'Secrets'.")
    st.info("Andá a Settings > Secrets en Streamlit Cloud y pegá el código [connections.gsheets]")
    st.stop() # Detiene la app aquí para no seguir con errores

# 4. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)
URL_HOJA = "https://docs.google.com/spreadsheets/d/16yNdj9OJZuTlnKya1wbtTRV_Px7NNjNR0qEr7ePPax4/edit" # ASEGURATE DE QUE ESTA URL SEA LA CORRECTA

try:
    # Leemos la hoja
    df_clientes = conn.read(spreadsheet=URL_HOJA)
    df_clientes.columns = df_clientes.columns.str.strip()
    st.success("✅ Conexión exitosa con Google Sheets")
    
    # Buscador simple para probar
    busqueda = st.text_input("Buscar Cliente:")
    if busqueda:
        resultado = df_clientes[df_clientes['Cliente'].str.contains(busqueda, case=False, na=False)]
        st.dataframe(resultado)
    else:
        st.dataframe(df_clientes)

except Exception as e:
    st.error(f"Fallo al leer los datos: {e}")