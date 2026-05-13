import os
import json
import psycopg2

# =========================
# CONFIGURACIÓN DB
# =========================

DB_NAME = os.environ.get("DB_NAME", "agentdb")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "password")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

# =========================
# CONEXIÓN
# =========================

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)

cursor = conn.cursor()

# =========================
# INIT DB
# =========================

def init_storage():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS libros (
        id SERIAL PRIMARY KEY,
        titulo TEXT,
        link TEXT UNIQUE,
        pdf TEXT,
        dominio TEXT,
        categoria TEXT,
        fuente TEXT,
        estado TEXT DEFAULT 'pendiente'
    )
    """)
    conn.commit()

# =========================
# INSERT LIBRO
# =========================

def guardar_libro(libro):
    """
    libro = {
        titulo,
        link,
        pdf,
        dominio,
        categoria,
        fuente
    }
    """

    try:
        cursor.execute("""
            INSERT INTO libros (titulo, link, pdf, dominio, categoria, fuente)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (link) DO NOTHING
        """, (
            libro["titulo"],
            libro["link"],
            libro["pdf"],
            libro["dominio"],
            libro["categoria"],
            libro["fuente"]
        ))

        conn.commit()
        return True

    except Exception as e:
        print("ERROR STORAGE:", str(e))
        conn.rollback()
        return False

# =========================
# OBTENER PENDIENTES
# =========================

def obtener_libros_pendientes(limit=10):
    cursor.execute("""
        SELECT id, titulo, link, pdf, dominio, categoria, fuente
        FROM libros
        WHERE estado = 'pendiente'
        LIMIT %s
    """, (limit,))

    return cursor.fetchall()

# =========================
# ACTUALIZAR ESTADO
# =========================

def actualizar_estado(libro_id, estado):
    cursor.execute("""
        UPDATE libros
        SET estado = %s
        WHERE id = %s
    """, (estado, libro_id))

    conn.commit()

# =========================
# OBTENER POR DOMINIO
# =========================

def obtener_por_dominio(dominio, limit=10):
    cursor.execute("""
        SELECT * FROM libros
        WHERE dominio = %s
        LIMIT %s
    """, (dominio, limit))

    return cursor.fetchall()

# =========================
# ESTADÍSTICAS BÁSICAS
# =========================

def stats():
    cursor.execute("""
        SELECT dominio, COUNT(*)
        FROM libros
        GROUP BY dominio
    """)

    return cursor.fetchall()

# =========================
# SHUTDOWN SAFE
# =========================

def cerrar():
    cursor.close()
    conn.close()
