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
    # 1. Leemos la hoja normalmente
    datos = conn.read(spreadsheet=URL_HOJA, usecols=[0, 1, 2])
    
    # 2. ESTA ES LA LÍNEA QUE DEBES AGREGAR:
    # Elimina los espacios antes o después de los nombres de las columnas
    datos.columns = datos.columns.str.strip()
    
    return datos

df_inventario = leer_inventario()





# --- ALERTAS DE STOCK (VERSIÓN SEGURA) ---
st.subheader("⚠️ Alertas de Reposición")

# 1. Verificamos si la columna existe en la tabla que viene de Google
columnas_reales = df_inventario.columns.tolist()

if "Cantidad" in columnas_reales:
    # 2. Forzamos a que los datos sean números (por si hay un texto accidental)
    df_inventario["Cantidad"] = pd.to_numeric(df_inventario["Cantidad"], errors='coerce').fillna(0)
    
    # 3. Recién ahora hacemos la comparación
    stock_bajo = df_inventario[df_inventario["Cantidad"] <= 5]
    
    if not stock_bajo.empty:
        for _, fila in stock_bajo.iterrows():
            st.warning(f"Poco stock: **{fila['Producto']}** ({int(fila['Cantidad'])} unidades)")
    else:
        st.success("✅ Stock suficiente en todos los productos.")
else:
    # 4. Si no la encuentra, te mostramos qué columnas sí está viendo Python
    st.error(f"No encuentro la columna 'Cantidad'.")
    st.write("Las columnas que detecto en tu Excel son:", columnas_reales)



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


# --- VISTA GENERAL Y BUSCADOR ---
st.divider()
st.subheader("🔍 Buscar en el Inventario")

# Creamos el campo de búsqueda
busqueda = st.text_input("Escribe el nombre del producto para filtrar:")

# Aplicamos el filtro si hay algo escrito
if busqueda:
    # Filtramos: el nombre del producto debe contener el texto buscado
    # .str.contains hace la magia, y case=False ignora mayúsculas
    df_filtrado = df_inventario[df_inventario["Producto"].str.contains(busqueda, case=False, na=False)]
else:
    # Si no hay nada escrito, mostramos todo
    df_filtrado = df_inventario

# Mostramos la tabla (filtrada o completa)
st.dataframe(df_filtrado, use_container_width=True)

# Información extra: cantidad de resultados
if busqueda:
    st.caption(f"Se encontraron {len(df_filtrado)} coincidencias.")