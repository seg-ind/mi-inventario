import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Inventario Nube", page_icon="☁️")
st.title("☁️ Inventario en la Nube (Google Sheets)")

# URL de tu Google Sheet
URL_HOJA = "https://docs.google.com/spreadsheets/d/1JuRSbWL5BmRKfHMhr-EKGOBbnIzL1uqhXISkT7rIrvs/edit?usp=sharing"

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_inventario():
    try:
        # Leemos las primeras 3 columnas
        datos = conn.read(spreadsheet=URL_HOJA, usecols=[0, 1, 2])
        # Limpiamos espacios en los nombres de columnas
        datos.columns = datos.columns.str.strip()
        # Aseguramos que la columna Producto sea tratada como texto siempre
        if "Producto" in datos.columns:
            datos["Producto"] = datos["Producto"].astype(str)
        return datos
    except Exception as e:
        st.error(f"Error al leer la hoja: {e}")
        return pd.DataFrame(columns=["Producto", "Cantidad", "Precio"])

df_inventario = leer_inventario()

# --- ALERTAS DE STOCK ---
st.subheader("⚠️ Alertas de Reposición")
if "Cantidad" in df_inventario.columns:
    # Convertimos a número para comparar
    df_inventario["Cantidad"] = pd.to_numeric(df_inventario["Cantidad"], errors='coerce').fillna(0)
    stock_bajo = df_inventario[df_inventario["Cantidad"] <= 5]
    
    if not stock_bajo.empty:
        for _, fila in stock_bajo.iterrows():
            st.warning(f"Poco stock: **{fila['Producto']}** ({int(fila['Cantidad'])} unidades)")
    else:
        st.success("✅ Todo en orden.")

st.divider()

# --- FORMULARIO DE CARGA ---
with st.form("gestion"):
    st.subheader("Cargar o Actualizar Producto")
    nombre = st.text_input("Nombre del Producto")
    cantidad = st.number_input("Cantidad", min_value=0)
    precio = st.number_input("Precio", min_value=0.0)
    if st.form_submit_button("Guardar Cambios"):
        if nombre:
            # Filtramos para no duplicar
            df_actualizado = df_inventario[df_inventario["Producto"].str.upper() != nombre.upper()]
            nueva_fila = pd.DataFrame({"Producto": [nombre], "Cantidad": [cantidad], "Precio": [precio]})
            df_final = pd.concat([df_actualizado, nueva_fila], ignore_index=True)
            conn.update(spreadsheet=URL_HOJA, data=df_final)
            st.success("¡Sincronizado!")
            st.rerun()

st.divider()

# --- BUSCADOR Y TABLA ---
st.subheader("🔍 Buscador de Inventario")
busqueda = st.text_input("Buscar producto por nombre:")

if busqueda:
    # Filtro seguro: convertimos a minúsculas para comparar
    df_filtrado = df_inventario[df_inventario["Producto"].str.contains(busqueda, case=False, na=False)]
else:
    df_filtrado = df_inventario

st.dataframe(df_filtrado, use_container_width=True)