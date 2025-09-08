import os
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Inicializar FastAPI
app = FastAPI()

# ✅ Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nerd-lat-dh-log-stica-j97fwz5c.netlify.app",  # tu frontend en Netlify
        "http://localhost:5173",  # para pruebas locales (vite/react)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE
    allow_headers=["*"],  # Permite todos los headers
)

# Ruta del archivo maestro
BASE_DIR = "data"
ARCHIVO_MAESTRO = "Matriz de Datos Integral.xlsx"

# Hojas que vamos a usar del Excel
BASES = {
    "reciclaje": "CentrodeReiclaje",
    "diferencia_modelos": "DiferenciaModelos",
    "costos": "Centro de Costos",
    "viajes": "Control de Viajes",
    "satisfaccion": "Base de Datos Satisfacción",
    "servicios": "Base de Datos Servicios Emp&Emb"
}

# Columnas esperadas para cada hoja
COLUMNAS_INICIALES = {
    "reciclaje": ["Viaje", "Placa", "Producto", "Componente", "Unidades", "Kg"],
    "diferencia_modelos": ["Modelo", "ImpactoContaminacionKg", "ImpactoContaminacion%", "CostosCOP", "Costos%"],
    "costos": ["Viaje", "Placa", "Producto", "Modelo", "CostosCOP"],
    "viajes": ["Viaje", "Placa", "Producto", "Fecha", "Cantidad"],
    "satisfaccion": ["Encuesta", "Cliente", "Calificacion", "Comentario"],
    "servicios": ["Viaje", "Placa", "Producto", "TipoEmpaque", "TiempoMin", "CostoCOP"],
}

def cargar_base(nombre_base, hoja, columnas):
    """Carga una hoja del archivo maestro y limpia columnas."""
    ruta = os.path.join(BASE_DIR, ARCHIVO_MAESTRO)
    df = pd.read_excel(ruta, sheet_name=hoja)
    df.columns = columnas[:len(df.columns)]
    return df

@app.get("/")
def home():
    return {"status": "Backend activo 🚀", "endpoints": list(BASES.keys())}

# Crear dinámicamente endpoints para cada hoja
for nombre_base, hoja in BASES.items():
    columnas = COLUMNAS_INICIALES[nombre_base]

    def endpoint(nombre=nombre_base, hoja=hoja, columnas=columnas):
        df = cargar_base(nombre, hoja, columnas)
        return df.to_dict(orient="records")

    app.get(f"/{nombre_base}")(endpoint)






