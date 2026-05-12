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

vistos = set()

# =========================
# DOMINIOS
# =========================

DOMINIOS = [
    "mathematics", "algebra", "geometry", "topology", "analysis",
    "number theory", "combinatorics", "graph theory",
    "probability", "statistics", "physics",
    "computer science", "machine learning",
    "chemistry", "biology", "neuroscience"
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
    if "machine learning" in t:
        return "cs"
    if "statistics" in t or "probability" in t:
        return "estadistica"

    return "matematicas"

# =========================
# FUENTE 1: ARXIV
# =========================

def fetch_arxiv(query, max_results=15):
    query = quote(query)

    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query=all:{query}&start=0&max_results={max_results}"
    )

    try:
        feed = feedparser.parse(url)
        return feed.entries
    except:
        return []

def normalizar_arxiv(entry):
    titulo = getattr(entry, "title", "")
    link = getattr(entry, "id", "")

    pdf = None
    if hasattr(entry, "links"):
        for l in entry.links:
            if "pdf" in l.get("href", ""):
                pdf = l.get("href")

    return {
        "titulo": titulo,
        "link": link,
        "pdf": pdf
    }

# =========================
# FUENTE 2: SEMANTIC SCHOLAR
# =========================

def fetch_semantic(query, max_results=15):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"

    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,url,openAccessPdf"
    }

    try:
        r = requests.get(url, params=params)
        return r.json().get("data", [])
    except:
        return []

def normalizar_semantic(entry):
    return {
        "titulo": entry.get("title", ""),
        "link": entry.get("url", ""),
        "pdf": (entry.get("openAccessPdf") or {}).get("url")
    }

# =========================
# FUENTE 3: OPENALEX
# =========================

def fetch_openalex(query, max_results=15):
    url = "https://api.openalex.org/works"

    params = {
        "search": query,
        "per-page": max_results
    }

    try:
        r = requests.get(url, params=params)
        return r.json().get("results", [])
    except:
        return []

def normalizar_openalex(entry):
    return {
        "titulo": entry.get("display_name", ""),
        "link": entry.get("id", ""),
        "pdf": None
    }

# =========================
# VALIDACIÓN
# =========================

def es_valido(item):
    if not item["link"]:
        return False

    if item["link"] in vistos:
        return False

    return True

# =========================
# ROUTER
# =========================

def elegir_fuente(dominio):
    d = dominio.lower()

    if d in ["mathematics", "physics"]:
        return "arxiv"

    if d in ["machine learning", "computer science"]:
        return "semantic"

    return "openalex"

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
        "message": "update agent knowledge system",
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
    dominio = random.choice(DOMINIOS)

    fuente = elegir_fuente(dominio)

    print("DOMINIO:", dominio)
    print("FUENTE:", fuente)

    if fuente == "arxiv":
        raw = fetch_arxiv(dominio)
        items = [normalizar_arxiv(x) for x in raw]

    elif fuente == "semantic":
        raw = fetch_semantic(dominio)
        items = [normalizar_semantic(x) for x in raw]

    else:
        raw = fetch_openalex(dominio)
        items = [normalizar_openalex(x) for x in raw]

    for item in items:

        if not es_valido(item):
            continue

        vistos.add(item["link"])

        categoria = clasificar(item["titulo"])

        cajas[categoria].append({
            "nombre": item["titulo"],
            "link": item["link"],
            "pdf": item["pdf"],
            "fuente": fuente,
            "dominio": dominio
        })

        print("CARGADO:", item["titulo"], "|", categoria)

    return guardar_en_github(cajas)

# =========================
# LOOP AGENTE
# =========================

def agente():
    print("INICIO AGENTE MULTIFUENTE")

    while True:
        try:
            procesar()
        except Exception as e:
            print("ERROR:", str(e))

        time.sleep(30)

# =========================
# ENTRYPOINT
# =========================

if __name__ == "__main__":
    agente()
