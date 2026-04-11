import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración y Conexión
st.set_page_config(page_title="Inventario Nube", page_icon="☁️")
st.title("☁️ Inventario en la Nube (Google Sheets)")

URL_HOJA = "https://docs.google.com/spreadsheets/d/TU_ID_DE_HOJA_AQUI/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Función de lectura (Limpia espacios y errores de texto)
def leer_inventario():
    try:
        datos = conn.read(spreadsheet=URL_HOJA, usecols=[0, 1, 2])
        datos.columns = datos.columns.str.strip() # Quita espacios como "Cantidad "
        if "Producto" in datos.columns:
            datos["Producto"] = datos["Producto"].astype(str).str.strip()
        return datos
    except Exception as e:
        return pd.DataFrame(columns=["Producto", "Cantidad", "Precio"])

df_inventario = leer_inventario()

# 3. Alertas de Stock Bajo
st.subheader("⚠️ Alertas de Reposición")
if "Cantidad" in df_inventario.columns:
    df_inventario["Cantidad"] = pd.to_numeric(df_inventario["Cantidad"], errors='coerce').fillna(0)
    stock_bajo = df_inventario[df_inventario["Cantidad"] <= 5]
    if not stock_bajo.empty:
        for _, fila in stock_bajo.iterrows():
            st.warning(f"Poco stock: **{fila['Producto']}** ({int(fila['Cantidad'])} unidades)")
    else:
        st.success("✅ Todo en orden.")

st.divider()

# 4. FORMULARIO DE GESTIÓN (Todo el bloque dentro del 'with')
with st.form("mi_formulario"):
    st.subheader("Cargar o Actualizar Producto")
    nombre_input = st.text_input("Nombre del Producto")
    cantidad_input = st.number_input("Cantidad", min_value=0, step=1)
    precio_input = st.number_input("Precio", min_value=0.0)
    
    # El botón DEBE estar dentro del 'with'
    boton_guardar = st.form_submit_button("Guardar Cambios")

    if boton_guardar:
        if nombre_input:
            nombre_l = nombre_input.strip()
            # Quitamos el viejo si existe (para actualizar)
            df_sin_actual = df_inventario[df_inventario["Producto"].str.upper() != nombre_l.upper()].copy()
            # Creamos la nueva fila
            nueva_fila = pd.DataFrame({"Producto": [nombre_l], "Cantidad": [cantidad_input], "Precio": [precio_input]})
            # Unimos
            df_final = pd.concat([df_sin_actual, nueva_fila], ignore_index=True)
            
            # Subimos a Google
            conn.update(spreadsheet=URL_HOJA, data=df_final)
            st.success(f"Sincronizado: {nombre_l}")
            st.rerun()
        else:
            st.error("Falta el nombre del producto.")

st.divider()

# 5. Buscador y Tabla
st.subheader("🔍 Buscador de Inventario")
busqueda = st.text_input("Escribe para filtrar:")

if busqueda:
    df_filtrado = df_inventario[df_inventario["Producto"].str.contains(busqueda, case=False, na=False)]
else:
    df_filtrado = df_inventario

st.dataframe(df_filtrado, use_container_width=True)