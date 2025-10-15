# 🏪 SuperMart Colombia - ETL Project

## 📋 Descripción
Proyecto desarrollado por **EAN TechRetail Solutions** para la empresa **SuperMart Colombia**, con el objetivo de construir un **pipeline ETL completo (Extract, Transform, Load)** en Python.

El sistema toma datos de ventas desde múltiples archivos CSV, los limpia, transforma, enriquece y genera información analítica lista para la toma de decisiones.

---

## 🚀 Estructura del proyecto
```
SuperMart_ETL_Project_FULL/
│
├── ventas_crudas.csv                # Datos originales de ventas
├── productos.csv                    # Catálogo de productos
├── tiendas.csv                      # Catálogo de tiendas
│
├── ventas_transformadas.csv         # Datos limpios y enriquecidos
├── data_mart_ventas.csv             # Dataset agregado para análisis
├── resumen_ejecutivo.csv            # Resumen con métricas clave
├── reporte_ejecutivo.txt            # Reporte gerencial automatizado
│
├── grafico_ventas_por_ciudad.png
├── grafico_distribucion_por_categoria.png
├── grafico_transacciones_por_dia.png
├── histograma_montos_venta.png
│
└── etl_supermart.py                 # Script principal del pipeline ETL
```

---

## 🧩 Tecnologías utilizadas
- **Python 3.8+**
- Librerías: `pandas`, `numpy`, `matplotlib`, `datetime`
- Entorno recomendado: Jupyter Notebook o ejecución directa por terminal

---

## ⚙️ Cómo ejecutar el pipeline
1. Coloca los tres archivos CSV (`ventas_crudas.csv`, `productos.csv`, `tiendas.csv`) en la misma carpeta que el script `etl_supermart.py`.
2. Abre una terminal en esa carpeta.
3. Ejecuta el comando:
   ```bash
   python etl_supermart.py
   ```
4. Se generarán automáticamente los archivos procesados, reportes y visualizaciones dentro del mismo directorio.

---

## 📈 Resultados automáticos
- **Dataset transformado:** datos limpios listos para análisis.
- **Data Mart:** agregaciones por ciudad, categoría y fecha.
- **Gráficos:** métricas visuales de ventas.
- **Reporte ejecutivo:** resumen textual con indicadores de calidad y top performers.

---

## 👨‍💻 Autor
**[Tu Nombre]**  
Ingeniero de Datos – EAN TechRetail Solutions

---

## 📄 Licencia
Este proyecto se distribuye bajo la licencia **MIT**, lo que permite su uso, modificación y distribución con atribución.
