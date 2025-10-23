# ==========================================================
# Proyecto: ETL - SuperMart Colombia
# Empresa: EAN TechRetail Solutions
# Rol: Ingeniero de Datos
# Autor: [Tu Nombre]
# Descripción:
#   Este script implementa un pipeline ETL completo (Extract, Transform, Load)
#   que limpia, transforma, integra y analiza los datos de ventas de SuperMart Colombia.
# ==========================================================

# ==========================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ==========================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
from textwrap import dedent

# ----------------------------------------------------------
# FUNCIONES AUXILIARES
# ----------------------------------------------------------

def safe_read_csv(path, **kwargs):
    """
    Lee un archivo CSV y maneja errores comunes.
    Devuelve el DataFrame y el estado de la carga.
    """
    try:
        df = pd.read_csv(path, **kwargs)
        status = "OK"
    except FileNotFoundError:
        df = pd.DataFrame()
        status = "ERROR: Archivo no encontrado"
    except pd.errors.ParserError as e:
        df = pd.DataFrame()
        status = f"ERROR de formato: {e}"
    return df, status


def write_text(path, text):
    """Guarda texto (por ejemplo, reportes) en un archivo."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

# ==========================================================
# 2. CONFIGURACIÓN INICIAL
# ==========================================================
# Carpeta de trabajo donde se crearán los archivos
base = "/mnt/data"

# ==========================================================
# 3. FASE DE EXTRACCIÓN (E)
# ==========================================================
# Objetivo: Cargar los datos desde múltiples fuentes (CSV) con manejo de errores.

# Definición de rutas de archivos
ventas_path = os.path.join(base, "ventas_crudas.csv")
productos_path = os.path.join(base, "productos.csv")
tiendas_path = os.path.join(base, "tiendas.csv")

# Lectura de CSVs
read_kwargs = dict(dtype={
    "order_id": "Int64",
    "producto_id": "string",
    "cantidad": "Int64",
    "precio_unitario": "float",
    "cliente_id": "string",
    "tienda_id": "string",
    "fecha": "string",
})
ventas_raw, s1 = safe_read_csv(ventas_path, **read_kwargs)
productos, s2 = safe_read_csv(productos_path)
tiendas, s3 = safe_read_csv(tiendas_path)

# Estadísticas de carga
print("\n===== FASE 1: EXTRACCIÓN =====")
print(f"Ventas: {len(ventas_raw)} registros | Estado: {s1}")
print(f"Productos: {len(productos)} registros | Estado: {s2}")
print(f"Tiendas: {len(tiendas)} registros | Estado: {s3}")

# ==========================================================
# 4. FASE DE TRANSFORMACIÓN (T)
# ==========================================================
# Objetivo: Limpiar, estandarizar y enriquecer los datos para análisis.

df = ventas_raw.copy()

# --- Limpieza de fechas ---
# Algunas fechas vienen en formatos distintos ("YYYY-MM-DD", "DD-MM-YYYY")
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", format="%Y-%m-%d") \
    .combine_first(pd.to_datetime(df["fecha"], errors="coerce", format="%d-%m-%Y"))

# --- Completar valores nulos ---
df["cliente_id"] = df["cliente_id"].fillna("CLIENTE_DESCONOCIDO")

# --- Eliminar duplicados ---
duplicated_ids = df[df["order_id"].duplicated(keep="first")]["order_id"].tolist()
df = df.drop_duplicates(subset=["order_id"], keep="first")

# --- Cálculo de métricas ---
df["venta_total"] = (df["cantidad"].astype(float) * df["precio_unitario"].astype(float)).round(2)

# --- Clasificación de ventas ---
bins = [-np.inf, 20, 50, np.inf]
labels = ["Baja", "Media", "Alta"]
df["categoria_venta"] = pd.cut(df["venta_total"], bins=bins, labels=labels, right=False)

# --- Enriquecimiento con catálogos ---
df = df.merge(productos, on="producto_id", how="left", validate="m:1")
df = df.merge(tiendas, on="tienda_id", how="left", validate="m:1")

# --- Dimensiones temporales ---
weekday_map = {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}
df["anio"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month
df["dia_semana"] = df["fecha"].dt.dayofweek.map(weekday_map)

# --- Control de calidad ---
quality = {
    "Registros Totales": len(df),
    "Duplicados Removidos": len(duplicated_ids),
    "Fechas Válidas": df["fecha"].notna().sum(),
    "Cantidades Positivas": (df["cantidad"] > 0).sum(),
    "Precios Positivos": (df["precio_unitario"] > 0).sum(),
    "Productos No Encontrados": df["categoria"].isna().sum(),
    "Tiendas No Encontradas": df["ciudad"].isna().sum()
}
print("\n===== FASE 2: TRANSFORMACIÓN =====")
for k,v in quality.items(): print(f"{k}: {v}")

# ==========================================================
# 5. FASE DE CARGA (L)
# ==========================================================
# Objetivo: Exportar los resultados limpios, optimizados y resumidos.

# --- Dataset transformado completo ---
dataset_path = os.path.join(base, "ventas_transformadas.csv")
df.to_csv(dataset_path, index=False)
print(f"\nArchivo transformado guardado en: {dataset_path}")

# --- Data Mart agregado ---
data_mart = (
    df.groupby(["fecha","anio","mes","dia_semana","ciudad","region","categoria"])
      .agg(transacciones=("order_id","count"),
           unidades=("cantidad","sum"),
           ventas=("venta_total","sum"))
      .reset_index()
)
data_mart_path = os.path.join(base, "data_mart_ventas.csv")
data_mart.to_csv(data_mart_path, index=False)
print(f"Data Mart guardado en: {data_mart_path}")

# --- Resumen ejecutivo ---
resumen = pd.DataFrame({
    "Métrica": ["Ventas Totales","Transacciones","Ticket Promedio","Clientes Únicos","Top Ciudad","Top Categoría"],
    "Valor": [
        round(df["venta_total"].sum(),2),
        df["order_id"].nunique(),
        round(df["venta_total"].mean(),2),
        df["cliente_id"].nunique(),
        df.groupby("ciudad")["venta_total"].sum().idxmax(),
        df.groupby("categoria")["venta_total"].sum().idxmax()
    ]
})
resumen_path = os.path.join(base, "resumen_ejecutivo.csv")
resumen.to_csv(resumen_path, index=False)
print(f"Resumen ejecutivo guardado en: {resumen_path}")

# ==========================================================
# 6. FASE DE ANÁLISIS Y VISUALIZACIONES
# ==========================================================
# Objetivo: Crear gráficos que ayuden a comprender el desempeño comercial.

plt.figure()
df.groupby("ciudad")["venta_total"].sum().plot(kind="bar")
plt.title("Ventas totales por ciudad")
plt.tight_layout()
plt.savefig(os.path.join(base,"grafico_ventas_por_ciudad.png"))

plt.figure()
df.groupby("categoria")["venta_total"].sum().plot(kind="pie", autopct="%1.1f%%")
plt.title("Distribución de ventas por categoría")
plt.tight_layout()
plt.savefig(os.path.join(base,"grafico_distribucion_por_categoria.png"))

plt.figure()
df.groupby("dia_semana")["order_id"].count().plot(kind="bar")
plt.title("Transacciones por día de la semana")
plt.tight_layout()
plt.savefig(os.path.join(base,"grafico_transacciones_por_dia.png"))

plt.figure()
plt.hist(df["venta_total"], bins=10)
plt.title("Distribución de montos de venta")
plt.tight_layout()
plt.savefig(os.path.join(base,"histograma_montos_venta.png"))

print("\nGráficos generados correctamente.")

# ==========================================================
# 7. REPORTE EJECUTIVO
# ==========================================================
# Objetivo: Documentar los resultados en un archivo de texto para la gerencia.

reporte_txt = f"""
REPORTE EJECUTIVO – SuperMart Colombia
Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

1) Métricas principales:
- Ventas Totales: ${df['venta_total'].sum():,.2f}
- Transacciones: {df['order_id'].nunique()}
- Ticket Promedio: ${df['venta_total'].mean():.2f}
- Clientes Únicos: {df['cliente_id'].nunique()}

2) Top Performers:
- Ciudad líder: {df.groupby('ciudad')['venta_total'].sum().idxmax()}
- Categoría líder: {df.groupby('categoria')['venta_total'].sum().idxmax()}

3) Indicadores de calidad de datos:
{quality}

4) Archivos generados:
- Dataset transformado: {dataset_path}
- Data Mart: {data_mart_path}
- Resumen ejecutivo: {resumen_path}
- Gráficos: carpeta {base}
"""
reporte_path = os.path.join(base, "reporte_ejecutivo.txt")
write_text(reporte_path, reporte_txt)
print(f"\nReporte generado en: {reporte_path}")

# ==========================================================
# FIN DEL PIPELINE
# ==========================================================
print("\n===== PIPELINE ETL COMPLETADO EXITOSAMENTE =====")
