# TecYMetAvCsD — Análisis de precios de WTI y Brent

Proyecto de limpieza, validación y análisis exploratorio de precios diarios de petróleo WTI y Brent, obtenidos mediante la API de EIA. Los precios se expresan en dólares estadounidenses por barril.

## Versión de Python

Los notebooks se desarrollaron y ejecutaron con **Python 3.11.9** en un entorno virtual local llamado `.venv`.

Para reproducir el trabajo, se recomienda utilizar esa misma versión de Python. Las dependencias se encuentran en `requirements.txt`: pandas, NumPy, requests, Matplotlib, JupyterLab, ipykernel y nbconvert. Ese archivo instala las bibliotecas; Python debe estar instalado previamente.

## Períodos de análisis

- **Período 1:** del 1 de enero de 2024 al 28 de febrero de 2026. Archivo: `notebooks/periodo_1_wti_brent.ipynb`.
- **Período 2:** del 1 de abril de 2026 hasta la fecha en que se ejecute el notebook. Archivo: `notebooks/periodo_2_wti_brent.ipynb`.

Marzo de 2026 queda fuera de los períodos definidos. La fecha final efectivamente disponible depende de las publicaciones de EIA y puede ser anterior a la fecha de ejecución.

Ambos notebooks siguen la misma estructura: limpieza y validación, cobertura temporal, medidas de tendencia central y dispersión, evolución de precios, spread Brent−WTI, retornos, volatilidad, base 100, diagramas de caja, movimientos extremos y autocorrelación. Cada gráfico incluye una explicación. El trabajo actual es exploratorio; no incluye un modelo predictivo.

La regresión lineal de precio contra días calendario se presenta en `notebooks/regresion_tiempo_precios_wti_brent.ipynb`. Usa el CSV local de `data/`, ajusta una recta para cada crudo y período, e informa la ecuación, R y R² junto con gráficos e interpretación. No requiere la clave de EIA; al ejecutarlo nuevamente usa el CSV de precios diarios más recientemente modificado.

## Instalación en Windows

Después de clonar o descargar el repositorio, abrir PowerShell en la carpeta que contiene este README y `requirements.txt`.

### 1. Verificar Python y crear el entorno

```powershell
python --version
python -m venv .venv
```

El primer comando debe mostrar la versión de Python que se utilizará para crear el entorno. En este proyecto se utilizó `Python 3.11.9`.

### 2. Instalar las dependencias

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Los comandos usan directamente el Python del entorno, por lo que no es necesario activarlo en PowerShell. `requirements.txt` define rangos de versiones compatibles; no fija una copia exacta de todas las versiones instaladas originalmente.

### 3. Configurar la clave de EIA

Crear un archivo llamado `secret_api_key.txt` en la raíz del repositorio, al mismo nivel que este README y `requirements.txt`. Dentro debe aparecer únicamente la clave personal de la API, en una sola línea, sin comillas ni el prefijo `api_key=`.

Ejemplo de contenido (reemplazar por la clave real):

```text
TU_API_KEY_DE_EIA
```

La ubicación debe quedar así:

```text
TecYMetAvCsD/
├── README.md
├── requirements.txt
├── .gitignore
├── secret_api_key.txt          # Archivo local: no se sube a GitHub
├── .venv/                     # Entorno local: no se sube a GitHub
└── notebooks/
    ├── periodo_1_wti_brent.ipynb
    └── periodo_2_wti_brent.ipynb
```

Cada integrante debe configurar su propia clave localmente. Se necesita conexión a Internet para instalar las dependencias y consultar la API.

### 4. Abrir y ejecutar los notebooks

Registrar un kernel dentro del entorno y abrir JupyterLab:

```powershell
.\.venv\Scripts\python.exe -m ipykernel install --sys-prefix --name petroleo-py311 --display-name "Python 3.11 (Petroleo)"
.\.venv\Scripts\python.exe -m jupyterlab
```

En JupyterLab, abrir uno de los notebooks de la carpeta `notebooks`, seleccionar el kernel **Python 3.11 (Petroleo)** y ejecutar todas las celdas en orden, desde el principio. Repetir el procedimiento para el otro período. Cada notebook puede ejecutarse de forma independiente.

Al volver a ejecutarlos, se consultan nuevamente los datos de EIA y se actualizan sus tablas, gráficos y explicaciones.

## Archivos para GitHub

Incluir en el commit el `README.md`, el `.gitignore`, el `requirements.txt` y los notebooks.

El `.gitignore` excluye `secret_api_key.txt` y `.venv/`. La clave y el entorno son locales: cada integrante crea los suyos siguiendo los pasos anteriores. Las salidas de los notebooks que se guarden dentro de los archivos `.ipynb` sí forman parte de esos archivos y se compartirán al subirlos.
