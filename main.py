from fastapi import FastAPI, UploadFile, File
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import pandas as pd
from io import BytesIO
import numpy as np
from typing import List, Dict

# Cargar variables del archivo .env
load_dotenv()

app = FastAPI()

# Conexión a MySQL
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

    conn = get_connection()
    if not conn:
        return {"error": "No se pudo conectar a MySQL"}

    cursor = conn.cursor()

    # Crear tabla si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS excel_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sheet_name VARCHAR(255),
            col1 VARCHAR(255),
            col2 VARCHAR(255),
            col3 VARCHAR(255)
        )
    """)

    # Limpiar datos y guardarlos
    for sheet, df in excel_data.items():
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(0, inplace=True)

        for _, row in df.iterrows():
            cursor.execute(
                "INSERT INTO excel_data (sheet_name, col1, col2, col3) VALUES (%s, %s, %s, %s)",
                (sheet, str(row[0]), str(row[1]), str(row[2]))
            )

    conn.commit()
    conn.close()

    return {"mensaje": "Datos guardados en MySQL ✅"}

@app.get("/data")
def get_data():
    conn = get_connection()
    if not conn:
        return {"error": "No se pudo conectar a MySQL"}

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM excel_data")
    data = cursor.fetchall()
    conn.close()

    return {"data": data}




