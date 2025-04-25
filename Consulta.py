# Librerías necesarias
import pandas as pd
import streamlit as st
import plotly.express as px

# Cargar el archivo CSV
archivo_csv = "Datos_Historicos_cuenta_al26032025.csv"
try:
    datos = pd.read_csv(archivo_csv)
    st.success("Archivo cargado exitosamente.")
except FileNotFoundError:
    st.error(f"Error: El archivo '{archivo_csv}' no se encontró.")
    st.stop()

# Verificar que las columnas necesarias existan
columnas_requeridas = ["Anio", "Categoria_Proyecto", "Ciclo", "Estado", "Tipo_Regimen_Hidrico", "Tipo_parcela", "Area_total_de_la_parcela(ha)"]
for columna in columnas_requeridas:
    if columna not in datos.columns:
        st.error(f"La columna '{columna}' no existe en el archivo CSV.")
        st.stop()

# Reemplazar valores nulos con "NA" para evitar problemas en los análisis
for columna in columnas_requeridas:
    datos[columna] = datos[columna].fillna("NA")

# Convertir la columna "Anio" a tipo numérico (si no lo es) para facilitar el análisis
datos["Anio"] = pd.to_numeric(datos["Anio"], errors="coerce")

# Convertir "Area_total_de_la_parcela(ha)" a numérico y reemplazar valores no válidos con 0
datos["Area_total_de_la_parcela(ha)"] = pd.to_numeric(datos["Area_total_de_la_parcela(ha)"], errors="coerce").fillna(0)

# Filtrar los datos para incluir solo los años en el rango deseado (2012-2025)
datos = datos[(datos["Anio"] >= 2012) & (datos["Anio"] <= 2025)]

# Calcular el número de observaciones por combinaciones de columnas clave
datos_agrupados = datos.groupby(
    ["Anio", "Categoria_Proyecto", "Ciclo", "Estado", "Tipo_Regimen_Hidrico", "Tipo_parcela"]
).size().reset_index(name="Observaciones")

# Título de la aplicación
st.title("Datos Históricos 2012-marzo2025. Bitácoras Agronómicas")

# Filtros
st.sidebar.header("Filtros")
categoria = st.sidebar.selectbox("Categoría del Proyecto:", ["Todos"] + list(datos_agrupados["Categoria_Proyecto"].unique()))
ciclo = st.sidebar.selectbox("Ciclo:", ["Todos"] + list(datos_agrupados["Ciclo"].unique()))
tipo_parcela = st.sidebar.selectbox("Tipo de Parcela:", ["Todos"] + list(datos_agrupados["Tipo_parcela"].unique()))
estado = st.sidebar.selectbox("Estado:", ["Todos"] + list(datos_agrupados["Estado"].unique()))
regimen = st.sidebar.selectbox("Régimen Hídrico:", ["Todos"] + list(datos_agrupados["Tipo_Regimen_Hidrico"].unique()))

# Filtrar datos según los filtros seleccionados
datos_filtrados = datos.copy()
if categoria != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Categoria_Proyecto"] == categoria]
if ciclo != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Ciclo"] == ciclo]
if tipo_parcela != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Tipo_parcela"] == tipo_parcela]
if estado != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Estado"] == estado]
if regimen != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Tipo_Regimen_Hidrico"] == regimen]

# Gráfico 1: Número de Bitácoras por Año
st.subheader("Número de Bitácoras por Año")
datos_agrupados_filtrados = datos_filtrados.groupby("Anio")["Observaciones"].sum().reset_index()
fig1 = px.bar(datos_agrupados_filtrados, x="Anio", y="Observaciones", title="Número de Bitácoras por Año")
st.plotly_chart(fig1)

# Gráfico 2: Superficie (ha) de las Parcelas por Año
st.subheader("Superficie (ha) de las Parcelas por Año")
datos_agrupados_area = datos_filtrados.groupby("Anio")["Area_total_de_la_parcela(ha)"].sum().reset_index()
fig2 = px.bar(datos_agrupados_area, x="Anio", y="Area_total_de_la_parcela(ha)", title="Superficie (ha) de las Parcelas por Año")
st.plotly_chart(fig2)

# Gráfico 3: Número de Parcelas por Año
if "Id_Parcela(Unico)" in datos_filtrados.columns:
    st.subheader("Número de Parcelas por Año")
    datos_agrupados_parcelas = datos_filtrados.groupby("Anio")["Id_Parcela(Unico)"].nunique().reset_index()
    fig3 = px.bar(datos_agrupados_parcelas, x="Anio", y="Id_Parcela(Unico)", title="Número de Parcelas por Año")
    st.plotly_chart(fig3)

# Gráfico 4: Número de Productores por Año
if "Id_Productor" in datos_filtrados.columns:
    st.subheader("Número de Productores por Año")
    datos_agrupados_productores = datos_filtrados.groupby("Anio")["Id_Productor"].nunique().reset_index()
    fig4 = px.bar(datos_agrupados_productores, x="Anio", y="Id_Productor", title="Número de Productores por Año")
    st.plotly_chart(fig4)

# Gráfico 5: Distribución por Género
if "Genero" in datos_filtrados.columns:
    st.subheader("Distribución (%) por Género de Productores(as)")
    datos_genero = datos_filtrados.groupby("Genero").size().reset_index(name="Registros")
    datos_genero["Porcentaje"] = (datos_genero["Registros"] / datos_genero["Registros"].sum()) * 100
    fig5 = px.pie(datos_genero, names="Genero", values="Porcentaje", title="Distribución (%) por Género de Productores(as)")
    st.plotly_chart(fig5)
