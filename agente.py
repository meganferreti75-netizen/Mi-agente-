import time
import json
import base64
import requests
import feedparser
from urllib.parse import quote

# =========================
# CONFIGURACIÓN
# =========================

GITHUB_TOKEN = "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"
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
    "ingenieria": []
}

# =========================
# ARXIV
# =========================

def buscar_libros(query="graph theory", max_results=5):
    query = quote(query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    feed = feedparser.parse(url)

    resultados = []

    for entry in feed.entries:
        resultados.append({
            "nombre": entry.title,
            "link": entry.id
        })

    return resultados

# =========================
# CLASIFICACIÓN
# =========================

def clasificar(texto):
    t = texto.lower()

    if any(k in t for k in ["graph", "algebra", "geometry", "number"]):
        return "matematicas"
    if "physics" in t:
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
# GITHUB (VERIFICADO)
# =========================

def guardar_en_github(data):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    contenido = json.dumps(data, ensure_ascii=False, indent=2)
    contenido_b64 = base64.b64encode(contenido.encode()).decode()

    # obtener SHA si existe
    r = requests.get(url, headers=headers)
    sha = None

    if r.status_code == 200:
        sha = r.json().get("sha")

    payload = {
        "message": "update libros agent",
        "content": contenido_b64,
        "branch": BRANCH
    }

    if sha:
        payload["sha"] = sha

    resp = requests.put(url, headers=headers, json=payload)

    # VERDAD DEL SISTEMA
    print("GITHUB STATUS:", resp.status_code)
    print("GITHUB RESPONSE:", resp.text)

    if resp.status_code in [200, 201]:
        return True
    else:
        return False

# =========================
# PIPELINE
# =========================

def procesar():
    resultados = buscar_libros("graph theory")

    for libro in resultados:
        categoria = clasificar(libro["nombre"])

        cajas[categoria].append({
            "nombre": libro["nombre"],
            "link": libro["link"]
        })

        print("PROCESANDO:", libro["nombre"])
        print("CLASIFICADO EN:", categoria)

    # persistencia validada
    ok = guardar_en_github(cajas)

    if ok:
        print("GUARDADO EN GITHUB CONFIRMADO")
    else:
        print("FALLO EN PERSISTENCIA")

# =========================
# AGENTE
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
