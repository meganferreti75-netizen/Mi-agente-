import time
import json
import base64
import requests
import feedparser
import os
from urllib.parse import quote
import random

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
# ESPACIO DE EXPLORACIÓN
# =========================

DOMINIOS = [

# =========================
# MATEMÁTICAS PURAS
# =========================
"mathematics",
"foundations of mathematics",
"mathematical logic",
"set theory",
"model theory",
"proof theory",
"recursion theory",
"category theory",
"algebra",
"linear algebra",
"abstract algebra",
"group theory",
"ring theory",
"field theory",
"representation theory",
"lie algebras",
"commutative algebra",
"homological algebra",
"geometry",
"euclidean geometry",
"differential geometry",
"algebraic geometry",
"non-euclidean geometry",
"topology",
"algebraic topology",
"differential topology",
"geometric topology",
"analysis",
"real analysis",
"complex analysis",
"functional analysis",
"harmonic analysis",
"measure theory",
"ergodic theory",
"operator theory",
"dynamical systems",
"chaos theory",
"fractal geometry",

# =========================
# TEORÍA DE NÚMEROS Y DISCRETA
# =========================
"number theory",
"analytic number theory",
"algebraic number theory",
"combinatorics",
"enumerative combinatorics",
"extremal combinatorics",
"probabilistic combinatorics",
"graph theory",
"theoretical computer science",
"discrete mathematics",

# =========================
# PROBABILIDAD Y ESTADÍSTICA
# =========================
"probability theory",
"stochastic processes",
"random walks",
"markov chains",
"statistics",
"mathematical statistics",
"inference theory",
"bayesian statistics",
"information theory",
"entropy",

# =========================
# FÍSICA FUNDAMENTAL
# =========================
"physics",
"classical mechanics",
"newtonian mechanics",
"lagrangian mechanics",
"hamiltonian mechanics",
"electromagnetism",
"optics",
"thermodynamics",
"statistical mechanics",
"fluid mechanics",
"plasma physics",

# =========================
# FÍSICA MODERNA
# =========================
"quantum mechanics",
"quantum field theory",
"particle physics",
"nuclear physics",
"high energy physics",
"relativity",
"general relativity",
"cosmology",
"astrophysics",
"condensed matter physics",

# =========================
# COMPUTACIÓN
# =========================
"computer science",
"algorithms",
"data structures",
"complexity theory",
"computability theory",
"automata theory",
"formal languages",
"programming languages",
"compiler theory",
"operating systems",
"distributed systems",
"databases",
"machine learning",
"deep learning",
"artificial intelligence",
"reinforcement learning",
"computer vision",
"natural language processing",
"robotics",
"cryptography",
"quantum computing",

# =========================
# INGENIERÍA
# =========================
"engineering",
"electrical engineering",
"mechanical engineering",
"civil engineering",
"chemical engineering",
"aerospace engineering",
"control theory",
"signal processing",
"systems engineering",
"robotic systems",

# =========================
# QUÍMICA
# =========================
"chemistry",
"physical chemistry",
"organic chemistry",
"inorganic chemistry",
"analytical chemistry",
"quantum chemistry",
"electrochemistry",
"chemical kinetics",
"materials science",

# =========================
# BIOLOGÍA
# =========================
"biology",
"molecular biology",
"cell biology",
"genetics",
"evolutionary biology",
"ecology",
"neuroscience",
"bioinformatics",
"biophysics",
"systems biology",

# =========================
# MEDICINA
# =========================
"medicine",
"clinical medicine",
"pathology",
"pharmacology",
"immunology",
"virology",
"epidemiology",
"public health",

# =========================
# CIENCIAS DE LA TIERRA
# =========================
"earth science",
"geology",
"geophysics",
"climatology",
"meteorology",
"oceanography",
"seismology",

# =========================
# ECONOMÍA Y SOCIALES CUANTITATIVAS
# =========================
"economics",
"microeconomics",
"macroeconomics",
"econometrics",
"game theory",
"social networks",
"complex networks",
"political science",
"sociology (quantitative)",
"behavioral economics",

# =========================
# INTERDISCIPLINARIO
# =========================
"complex systems",
"nonlinear systems",
"network science",
"data science",
"computational science",
"systems biology",
"computational neuroscience",
"mathematical biology",

# =========================
# FILOSOFÍA FORMAL
# =========================
"philosophy of science",
"epistemology",
"logic",
"formal epistemology",
"philosophy of mathematics"
]

# =========================
# ARXIV EXPANDIDO
# =========================

def buscar_libros(query, max_results=20):
    query = quote(query)

    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query=all:{query}"
        "&start=0"
        f"&max_results={max_results}"
    )

    try:
        feed = feedparser.parse(url)

        return [
            {
                "nombre": entry.title,
                "link": entry.id
            }
            for entry in feed.entries
        ]

    except Exception as e:
        print("ERROR ARXIV:", str(e))
        return []

# =========================
# CLASIFICACIÓN
# =========================

def clasificar(texto):
    t = texto.lower()

    if any(k in t for k in ["graph", "algebra", "geometry", "number", "topology"]):
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
    if "machine learning" in t:
        return "cs"
    if "statistics" in t or "probability" in t:
        return "estadistica"

    return "matematicas"

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

    return resp.status_code in [200, 201]

# =========================
# PIPELINE
# =========================

def procesar():
    query = random.choice(DOMINIOS)

    print("QUERY ACTUAL:", query)

    resultados = buscar_libros(query, max_results=20)

    for libro in resultados:
        categoria = clasificar(libro["nombre"])

        cajas[categoria].append({
            "nombre": libro["nombre"],
            "link": libro["link"]
        })

        print("PROCESANDO:", libro["nombre"])
        print("CLASIFICADO EN:", categoria)

    return guardar_en_github(cajas)

# =========================
# AGENTE
# =========================

def agente():
    print("INICIO DEL AGENTE EXPANDIDO")

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
