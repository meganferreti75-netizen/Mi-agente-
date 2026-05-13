import time
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
#
# =========================
# ROUTER INTELIGENTE
# =========================

def elegir_fuente(dominio):

    d = dominio.lower()

    matematicas = [
        "mathematics",
        "algebra",
        "geometry",
        "topology",
        "analysis",
        "number theory",
        "combinatorics",
        "graph theory",
        "probability",
        "statistics"
    ]

    fisica = [
        "physics"
    ]

    computacion = [
        "computer science",
        "machine learning"
    ]

    biologia = [
        "biology",
        "neuroscience"
    ]

    quimica = [
        "chemistry"
    ]

    # =========================
    # MATEMÁTICAS Y FÍSICA
    # =========================

    if d in matematicas or d in fisica:
        return random.choice([
            "arxiv",
            "semantic",
            "openalex"
        ])

    # =========================
    # COMPUTACIÓN
    # =========================

    if d in computacion:
        return random.choice([
            "semantic",
            "arxiv",
            "openalex"
        ])

    # =========================
    # BIOLOGÍA Y QUÍMICA
    # =========================

    if d in biologia or d in quimica:
        return random.choice([
            "semantic",
            "openalex"
        ])

    # =========================
    # DEFAULT
    # =========================

    return random.choice([
        "arxiv",
        "semantic",
        "openalex"
    
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

        guardar_libro({
    "titulo": item["titulo"],
    "link": item["link"],
    "pdf": item["pdf"],
    "dominio": dominio,
    "categoria": categoria,
    "fuente": fuente
})

        print("CARGADO:", item["titulo"], "|", categoria)

    from storage import guardar_libro, init_storage

# =========================
# LOOP AGENTE
# =========================

def agente():
    def agente():
    print("INICIO AGENTE MULTIFUENTE")

    init_storage()

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
