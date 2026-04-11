import streamlit as st
import pandas as pd
import os

# Configuración y constantes
ARCHIVO_DATOS = "inventario.csv"
LIMITE_STOCK_BAJO = 5  # Puedes cambiar este número según tu necesidad

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        return pd.read_csv(ARCHIVO_DATOS)
    else:
        return pd.DataFrame(columns=["Producto", "Cantidad", "Precio"])

def guardar_datos(df):
    df.to_csv(ARCHIVO_DATOS, index=False)

# --- Interfaz de la Aplicación ---
st.set_page_config(page_title="Control de Inventario", page_icon="📦")
st.title("📦 Control de Inventario")

df_inventario = cargar_datos()

# --- SECCIÓN DE ALERTAS ---
st.subheader("⚠️ Alertas de Reposición")
# Filtramos productos que tengan 5 o menos unidades
stock_bajo = df_inventario[df_inventario["Cantidad"] <= LIMITE_STOCK_BAJO]

if not stock_bajo.empty:
    for index, fila in stock_bajo.iterrows():
        st.warning(f"¡Atención! El producto **{fila['Producto']}** tiene solo **{fila['Cantidad']}** unidades.")
else:
    st.success("✅ Todos los productos tienen stock suficiente.")

st.divider()

# --- SECCIÓN PARA AGREGAR O ACTUALIZAR ---
st.subheader("Gestionar Productos")
with st.form("nuevo_producto"):
    nombre = st.text_input("Nombre del producto")
    cantidad = st.number_input("Cantidad actual", min_value=0, step=1)
    precio = st.number_input("Precio por unidad", min_value=0.0, format="%.2f")
    boton_agregar = st.form_submit_button("Actualizar Inventario")

    if boton_agregar:
        if nombre:
            # Si el producto ya existe, lo actualizamos; si no, lo añadimos
            if nombre in df_inventario["Producto"].values:
                df_inventario.loc[df_inventario["Producto"] == nombre, ["Cantidad", "Precio"]] = [cantidad, precio]
                mensaje = f"Producto '{nombre}' actualizado."
            else:
                nueva_fila = pd.DataFrame({"Producto": [nombre], "Cantidad": [cantidad], "Precio": [precio]})
                df_inventario = pd.concat([df_inventario, nueva_fila], ignore_index=True)
                mensaje = f"Producto '{nombre}' agregado."
            
            guardar_datos(df_inventario)
            st.success(mensaje)
            st.rerun()
        else:
            st.error("El nombre del producto es obligatorio.")

# --- VISTA GENERAL ---
st.subheader("Listado Completo")
st.dataframe(df_inventario, use_container_width=True)

if st.button("Vaciar Inventario"):
    if st.checkbox("Confirmar eliminación de todos los datos"):
        df_inventario = pd.DataFrame(columns=["Producto", "Cantidad", "Precio"])
        guardar_datos(df_inventario)
        st.rerun()