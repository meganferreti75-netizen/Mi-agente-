import os
import json
import time
import requests
import feedparser
import urllib.parse
from pypdf import PdfReader

# ==========================================
# CONFIG
# ==========================================

ESTADO_PATH = "estado_libros.json"
DOWNLOAD_DIR = "pdfs"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ==========================================
# MEMORIA / CAJAS
# ==========================================

def cargar_estado():

    if os.path.exists(ESTADO_PATH):

        with open(ESTADO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "matematicas": [],
        "fisica": [],
        "quimica": [],
        "biologia": [],
        "filosofia": [],
        "arte": [],
        "ingenieria": []
    }

def guardar_estado(cajas):

    with open(ESTADO_PATH, "w", encoding="utf-8") as f:
        json.dump(cajas, f, indent=2, ensure_ascii=False)

# ==========================================
# BUSCADOR ARXIV
# ==========================================

def buscar_libros(query="graph theory", max_results=10):

    query_encoded = urllib.parse.quote(query)

    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query=all:{query_encoded}"
        f"&start=0"
        f"&max_results={max_results}"
    )

    feed = feedparser.parse(url)

    resultados = []

    for entry in feed.entries:

        pdf_url = entry.id.replace("abs", "pdf") + ".pdf"

        resultados.append({
            "title": entry.title,
            "url": pdf_url
        })

    return resultados

# ==========================================
# DESCARGA PDF
# ==========================================

def descargar_pdf(url, nombre):

    try:

        path = os.path.join(DOWNLOAD_DIR, nombre + ".pdf")

        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            return None

        with open(path, "wb") as f:
            f.write(response.content)

        return path

    except Exception as e:

        print("ERROR DESCARGA:", e)

        return None

# ==========================================
# VALIDAR PDF
# ==========================================

def pdf_valido(path):

    try:

        reader = PdfReader(path)

        paginas = len(reader.pages)

        return paginas > 0

    except Exception as e:

        print("PDF CORRUPTO:", e)

        return False

# ==========================================
# CLASIFICADOR SIMPLE
# ==========================================

def clasificar(titulo):

    t = titulo.lower()

    if (
        "graph" in t or
        "algebra" in t or
        "geometry" in t or
        "theorem" in t or
        "math" in t
    ):
        return "matematicas"

    if (
        "physics" in t or
        "quantum" in t or
        "relativity" in t
    ):
        return "fisica"

    if (
        "chem" in t or
        "molecule" in t
    ):
        return "quimica"

    if (
        "bio" in t or
        "genetic" in t
    ):
        return "biologia"

    if (
        "philosophy" in t or
        "ethics" in t
    ):
        return "filosofia"

    if (
        "art" in t or
        "painting" in t
    ):
        return "arte"

    if (
        "engineering" in t or
        "system" in t
    ):
        return "ingenieria"

    return "matematicas"

# ==========================================
# EVITAR DUPLICADOS
# ==========================================

def ya_existe(cajas, nombre):

    for categoria in cajas.values():

        for item in categoria:

            if item["nombre"] == nombre:
                return True

    return False

# ==========================================
# PROCESAMIENTO
# ==========================================

def procesar_query(cajas, query):

    print("\n============================")
    print("BUSCANDO:", query)
    print("============================\n")

    resultados = buscar_libros(query=query, max_results=10)

    for libro in resultados:

        nombre = libro["title"]
        url = libro["url"]

        if ya_existe(cajas, nombre):

            print("YA EXISTE:", nombre)

            continue

        print("PROCESANDO:", nombre)

        safe_name = (
            nombre
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .replace(":", "_")
        )

        path = descargar_pdf(url, safe_name)

        if not path:

            print("NO DESCARGADO")

            continue

        valido = pdf_valido(path)

        if not valido:

            print("PDF INVALIDO")

            continue

        categoria = clasificar(nombre)

        cajas[categoria].append({
            "nombre": nombre,
            "link": url
        })

        guardar_estado(cajas)

        print("GUARDADO EN:", categoria)

# ==========================================
# AGENTE PRINCIPAL
# ==========================================

def agente():

    cajas = cargar_estado()

    queries = [

        "graph theory",
        "competitive programming",
        "number theory",
        "linear algebra",
        "algorithms",
        "data structures",
        "optimization",
        "machine learning",
        "geometry",
        "combinatorics"

    ]

    i = 0

    while True:

        query_actual = queries[i % len(queries)]

        try:

            procesar_query(cajas, query_actual)

        except Exception as e:

            print("ERROR GENERAL:", e)

        i += 1

        print("\nDURMIENDO 30 SEGUNDOS...\n")

        time.sleep(30)

# ==========================================
# RUN
# ==========================================

agente()
