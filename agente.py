import time
import json
import base64
import requests
import feedparser
from urllib.parse import quote

# =========================
# CONFIGURACIÓN GITHUB
# =========================

GITHUB_TOKEN = "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"
REPO = "meganferreti75-netizen/Agent-books"
FILE_PATH = "estado_libros.json"
BRANCH = "main"

# =========================
# ESTADO EN MEMORIA
# =========================

cajas = {
    "matematicas": [],
    "fisica": [],
    "quimica": [],
    "biologia": [],
    "filosofia": [],
    "arte": [],
    "ingenieria": []
}

# =========================
# BUSCADOR ARXIV
# =========================

def buscar_libros(query="graph theory", max_results=5):
    query = quote(query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    feed = feedparser.parse(url)

    resultados = []

    for entry in feed.entries:
        resultados.append({
            "titulo": entry.title,
            "link": entry.id,
            "resumen": entry.summary
        })

    return resultados

# =========================
# CLASIFICACIÓN SIMPLE
# =========================

def clasificar(texto):
    t = texto.lower()

    if any(k in t for k in ["graph", "algebra", "geometry", "number"]):
        return "matematicas"
    if "physics" in t or "quantum" in t:
        return "fisica"
    if "chem" in t:
        return "quimica"
    if "bio" in t:
        return "biologia"
    if "philosophy" in t:
        return "filosofia"
    if "engineering" in t:
        return "ingenieria"

    return "matematicas"

# =========================
# GUARDAR EN GITHUB
# =========================

def guardar_en_github(data):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    contenido = json.dumps(data, ensure_ascii=False, indent=2)
    contenido_b64 = base64.b64encode(contenido.encode()).decode()

    r = requests.get(url, headers=headers)
    sha = None
    if r.status_code == 200:
        sha = r.json()["sha"]

    payload = {
        "message": "update libros agent",
        "content": contenido_b64,
        "branch": BRANCH
    }

    if sha:
        payload["sha"] = sha

    requests.put(url, headers=headers, json=payload)

# =========================
# PROCESAMIENTO
# =========================

def procesar():
    resultados = buscar_libros("graph theory")

    for libro in resultados:
        categoria = clasificar(libro["titulo"])

        cajas[categoria].append({
            "nombre": libro["titulo"],
            "link": libro["link"]
        })

        print("GUARDADO EN:", categoria)

    guardar_en_github(cajas)

# =========================
# AGENTE PRINCIPAL
# =========================

def agente():
    print("INICIO DEL AGENTE")

    while True:
        procesar()
        time.sleep(30)

# =========================
# ENTRYPOINT
# =========================

if __name__ == "__main__":
    agente()
