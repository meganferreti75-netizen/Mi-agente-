import time
import json
import base64
import requests
import feedparser
import os
import random
from urllib.parse import quote

# =========================
# CONFIGURACIÓN
# =========================

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = "meganferreti75-netizen/Agent-books"
FILE_PATH = "estado_libros.json"
BRANCH = "main"

# =========================
# ESTADO
# =========================

cajas = {
    "matematicas": [],
    "fisica": [],
    "quimica": [],
    "biologia": [],
    "filosofia": [],
    "arte": [],
    "ingenieria": [],
    "cs": [],
    "estadistica": []
}

# =========================
# DOMINIOS
# =========================

DOMINIOS = [
    "mathematics", "algebra", "geometry", "topology", "analysis",
    "number theory", "combinatorics", "graph theory",
    "probability", "statistics", "stochastic processes",
    "physics", "quantum mechanics", "relativity",
    "computer science", "machine learning", "artificial intelligence",
    "optimization", "information theory",
    "chemistry", "biology", "neuroscience",
    "economics", "game theory",
    "logic", "category theory"
]

# =========================
# CLASIFICACIÓN
# =========================

def clasificar(texto):
    t = texto.lower()

    if any(k in t for k in ["graph", "algebra", "geometry", "topology", "number"]):
        return "matematicas"
    if "physics" in t:
        return "fisica"
    if "chem" in t:
        return "quimica"
    if "bio" in t or "neuro" in t:
        return "biologia"
    if "philosophy" in t:
        return "filosofia"
    if "engineering" in t:
        return "ingenieria"
    if "machine learning" in t or "artificial intelligence" in t:
        return "cs"
    if "statistics" in t or "probability" in t:
        return "estadistica"

    return "matematicas"

# =========================
# ARXIV
# =========================

def buscar_libros(query, max_results=20):
    query = quote(query)

    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query=all:{query}"
        "&start=0"
        f"&max_results={max_results}"
    )

    feed = feedparser.parse(url)
    return feed.entries

# =========================
# FILTRO DE "DOCUMENTO COMPLETO"
# =========================

def tiene_pdf(entry):
    if hasattr(entry, "links"):
        for l in entry.links:
            if "pdf" in l.get("href", ""):
                return True
    return False

def tiene_link(entry):
    return hasattr(entry, "id") and entry.id is not None

# =========================
# GITHUB
# =========================

def guardar_en_github(data):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    contenido = json.dumps(data, ensure_ascii=False, indent=2)
    contenido_b64 = base64.b64encode(contenido.encode()).decode()

    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None

    payload = {
        "message": "update libros agent",
        "content": contenido_b64,
        "branch": BRANCH
    }

    if sha:
        payload["sha"] = sha

    resp = requests.put(url, headers=headers, json=payload)

    print("GITHUB STATUS:", resp.status_code)

    if resp.status_code not in [200, 201]:
        print("ERROR:", resp.text)
        return False

    return True

# =========================
# PIPELINE
# =========================

def procesar():
    query = random.choice(DOMINIOS)
    print("QUERY:", query)

    entries = buscar_libros(query)

    for entry in entries:

        titulo = getattr(entry, "title", "")
        link = getattr(entry, "id", "")

        if not tiene_link(entry):
            print("RECHAZADO (sin link):", titulo)
            continue

        if not tiene_pdf(entry):
            print("RECHAZADO (sin PDF):", titulo)
            continue

        categoria = clasificar(titulo)

        cajas[categoria].append({
            "nombre": titulo,
            "link": link
        })

        print("CARGADO EN CAJA:", categoria)
        print("ITEM:", titulo)

    return guardar_en_github(cajas)

# =========================
# AGENTE
# =========================

def agente():
    print("INICIO DEL AGENTE")

    while True:
        try:
            ok = procesar()

            if ok:
                print("GUARDADO OK")
            else:
                print("ERROR GUARDANDO")

        except Exception as e:
            print("ERROR GENERAL:", str(e))

        time.sleep(30)

# =========================
# ENTRYPOINT
# =========================

if __name__ == "__main__":
    agente()
