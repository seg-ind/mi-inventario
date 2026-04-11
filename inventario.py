import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Inventario Nube", page_icon="☁️")
st.title("☁️ Inventario en la Nube (Google Sheets)")

# URL de tu Google Sheet (debes reemplazar esta por la tuya)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1JuRSbWL5BmRKfHMhr-EKGOBbnIzL1uqhXISkT7rIrvs/edit?usp=sharing"

# Establecer conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para leer datos
def leer_inventario():
    return conn.read(spreadsheet=URL_HOJA, usecols=[0, 1, 2])

df_inventario = leer_inventario()

# --- ALERTAS DE STOCK ---
st.subheader("⚠️ Alertas de Reposición")
stock_bajo = df_inventario[df_inventario["Cantidad"] <= 5]
if not stock_bajo.empty:
    for _, fila in stock_bajo.iterrows():
        st.warning(f"Quedan pocas unidades de: **{fila['Producto']}** ({fila['Cantidad']})")
else:
    st.success("Stock en niveles óptimos.")

# --- FORMULARIO PARA AGREGAR ---
with st.form("gestion_inventario"):
    st.subheader("Cargar o Actualizar Producto")
    nombre = st.text_input("Nombre del Producto")
    cantidad = st.number_input("Cantidad", min_value=0)
    precio = st.number_input("Precio", min_value=0.0)
    boton = st.form_submit_button("Guardar Cambios")

    if boton:
        if nombre:
            # Si el producto ya existe, lo eliminamos de la lista vieja para poner el nuevo
            df_actualizado = df_inventario[df_inventario["Producto"] != nombre]
            nueva_fila = pd.DataFrame({"Producto": [nombre], "Cantidad": [cantidad], "Precio": [precio]})
            df_final = pd.concat([df_actualizado, nueva_fila], ignore_index=True)
            
            # Guardar en Google Sheets
            conn.update(spreadsheet=URL_HOJA, data=df_final)
            st.success("¡Datos sincronizados con Google Sheets!")
            st.rerun()

# --- TABLA GENERAL ---
st.subheader("Vista General del Inventario")
st.dataframe(df_inventario, use_container_width=True)