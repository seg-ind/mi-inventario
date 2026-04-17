import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Gestión Comercial", layout="wide")

st.markdown("""
    <style>
    .stButton>button { background-color: #002b5e; color: white; }
    h1 { color: #002b5e; }
    </style>
    """, unsafe_allow_html=True)

# 2. MANEJO DEL LOGO (Local)
ruta_logo = os.path.join(os.path.dirname(__file__), 'LOGO.jpg')
col_l, col_r = st.columns([1, 4])
with col_l:
    if os.path.exists(ruta_logo):
        st.image(ruta_logo, width=150)
    else:
        st.info("Logo no detectado")
with col_r:
    st.title("Gestión Comercial")

# 3. CONEXIÓN Y CARGA (Con blindaje de errores)
URL_HOJA = "TU_URL_DE_GOOGLE_SHEETS_AQUI" # <-- VERIFICÁ QUE ESTÉ TU LINK
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_base_clientes():
    try:
        df = conn.read(spreadsheet=URL_HOJA)
        # Limpiamos columnas de una forma agresiva para que no falle
        df.columns = [str(c).strip().upper().replace('Ó', 'O') for c in df.columns]
        
        # Renombramos para trabajar cómodos
        df = df.rename(columns={'ID': 'ID', 'CLIENTE': 'Cliente', 'UBICACION': 'Ubicacion'})
        
        if 'Cliente' in df.columns and 'Ubicacion' in df.columns:
            df['IDENTIFICACION'] = df['Cliente'].astype(str) + " - " + df['Ubicacion'].astype(str)
        return df
    except Exception as e:
        # Si falla, devolvemos una tabla vacía con las columnas necesarias para que no dé NameError
        return pd.DataFrame(columns=['ID', 'Cliente', 'Ubicacion', 'IDENTIFICACION'])

# Ejecutamos la carga
df_clientes = cargar_base_clientes()

# 4. BUSCADORES
st.markdown("---")
col_id, col_txt = st.columns(2)
with col_id:
    bus_id = st.text_input("Código del Cliente (ID):")
with col_txt:
    bus_txt = st.text_input("Identificación (Nombre o Ubicación):")

# 5. FILTRADO (Seguro contra tablas vacías)
if not df_clientes.empty:
    df_filtrado = df_clientes.copy()
    if bus_id:
        df_filtrado = df_filtrado[df_filtrado['ID'].astype(str).str.contains(bus_id, case=False)]
    if bus_txt:
        df_filtrado = df_filtrado[df_filtrado['IDENTIFICACION'].str.contains(bus_txt, case=False, na=False)]

    # 6. MOSTRAR RESULTADOS
    st.subheader("Resultados")
    if not df_filtrado.empty:
        for i, fila in df_filtrado.iterrows():
            c1, c2, c3 = st.columns([1, 3, 4])
            c1.write(fila['ID'])
            c2.write(fila['IDENTIFICACION'])
            with c3:
                cols = st.columns(6)
                cols[0].button("📄", key=f"b1_{i}")
                cols[1].button("🛠️", key=f"b2_{i}")
                cols[2].button("🚚", key=f"b3_{i}")
                cols[3].button("💰", key=f"b4_{i}")
                cols[4].button("📊", key=f"b5_{i}")
                cols[5].button("✉️", key=f"b6_{i}")
    else:
        st.info("No hay coincidencias.")
else:
    st.error("❌ No se pudo conectar con la base de datos o el Excel está vacío.")
    st.info("Verificá los Secrets en Streamlit Cloud y que el link de la hoja sea correcto.")