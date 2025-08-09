from fastapi import FastAPI, UploadFile, File
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import pandas as pd
from io import BytesIO
import numpy as np

# Cargar variables del archivo .env
load_dotenv()

app = FastAPI()

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="maglev.proxy.rlwy.net",
            port=40716,
            user="root",
            password="JxqVGHZZejEuCRifERUJGJFwKQUhwtSA",
            database="railway"
        )
        return connection
    except Error as e:
        print("Error de conexión:", e)
        return None

@app.get("/")
def read_root():
    return {"mensaje": "API conectada a FastAPI ✅"}

@app.get("/test-db")
def test_db():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        result = cursor.fetchone()
        conn.close()
        return {"Base de datos": result[0]}
    else:
        return {"error": "No se pudo conectar a MySQL"}

@app.post("/upload-excel/")
async def upload_excel(file: UploadFile = File(...)):
    contents = await file.read()
    excel_data = pd.read_excel(BytesIO(contents), sheet_name=None, header=1, usecols="B:D")

    cleaned_data = {}

    for sheet, df in excel_data.items():
        # Intentar convertir columnas numéricas y forzar NaN en errores
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Reemplazar infinitos y NaN
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(0, inplace=True)

        # Convertir a lista de diccionarios
        cleaned_data[sheet] = df.to_dict(orient="records")

    return {"data": cleaned_data}



