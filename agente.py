import time
import sqlite3
import random
from flask import Flask, jsonify
import threading

# =========================
# BASE DE DATOS
# =========================

conn = sqlite3.connect("libros.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS libros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tema TEXT,
    subtema TEXT,
    nombre TEXT,
    link TEXT,
    estado TEXT
)
""")

conn.commit()

vistos = set()

# =========================
# APP
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "SISTEMA DE TRANSFORMADORES ACTIVO"

@app.route("/libros")
def libros():
    cursor.execute("SELECT * FROM libros")
    return jsonify(cursor.fetchall())

# =========================
# BIBLIOTECA SIMULADA
# =========================

BIBLIOTECA = {
    "matematicas": ["algebra", "calculo", "geometria"],
    "fisica": ["mecanica", "optica", "termodinamica"],
    "quimica": ["organica", "inorganica"],
    "biologia": ["celular", "evolucion"]
}

# =========================
# VALIDACIÓN
# =========================

def es_valido(libro):
    if not libro["link"]:
        return False
    if libro["nombre"] in vistos:
        return False
    return True

# =========================
# GENERADOR DE LIBROS (SIMULADO)
# =========================

def buscar_libros(tema, subtema):
    return [
        {
            "tema": tema,
            "subtema": subtema,
            "nombre": f"{subtema}_libro_{i}",
            "link": f"http://libro/{subtema}/{i}"
        }
        for i in range(10)
    ]

# =========================
# TRANSFORMADOR (TRABAJADOR)
# =========================

def transformer(libro, tarea):
    return {
        "original": libro,
        "resultado": f"Resumen de {libro['nombre']} en {tarea}"
    }

# =========================
# EQUIPO (6 trabajadores virtuales)
# =========================

def equipo_transformador(libros, tareas):
    resultados = []

    for i, libro in enumerate(libros):
        tarea = tareas[i % len(tareas)]
        resultados.append(transformer(libro, tarea))

    return resultados

# =========================
# LÍDER (AGREGADOR)
# =========================

def lider(resultados):
    return {
        "resumen_general": [r["resultado"] for r in resultados]
    }

# =========================
# STORAGE
# =========================

def guardar(libro):
    cursor.execute("""
        INSERT INTO libros (tema, subtema, nombre, link, estado)
        VALUES (?, ?, ?, ?, ?)
    """, (
        libro["tema"],
        libro["subtema"],
        libro["nombre"],
        libro["link"],
        "guardado"
    ))

    conn.commit()
    vistos.add(libro["nombre"])

# =========================
# PROCESO DE TEMA
# =========================

def procesar_tema(tema, subtemas):
    resultados_totales = []

    for sub in subtemas:

        libros = buscar_libros(tema, sub)

        libros_validos = []

        for l in libros:
            if es_valido(l):
                guardar(l)
                libros_validos.append(l)

        tareas = ["analisis", "resumen", "estructura", "conceptos"]

        resultados = equipo_transformador(libros_validos, tareas)

        resumen = lider(resultados)

        resultados_totales.append({
            "subtema": sub,
            "resumen": resumen
        })

    return resultados_totales

# =========================
# ORQUESTADOR
# =========================

def orquestador():
    resultados_globales = {}

    for tema, subtemas in BIBLIOTECA.items():
        resultados_globales[tema] = procesar_tema(tema, subtemas)

    return resultados_globales

# =========================
# WORKER LOOP
# =========================

def worker():
    while True:
        try:
            print("EJECUTANDO ORQUESTADOR")
            orquestador()
        except Exception as e:
            print("ERROR:", e)

        time.sleep(30)

# =========================
# BOOT
# =========================

if __name__ == "__main__":

    threading.Thread(target=worker, daemon=True).start()

    port = 8000
    app.run(host="0.0.0.0", port=port)
