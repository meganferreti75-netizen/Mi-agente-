from supabase import create_client

SUPABASE_URL = "https://apdreukupdfbepxarkmy.supabase.co"
SUPABASE_KEY = "sb_publishable_d2UYyU7UEDxCn0mAPh4SGQ_Cp40LqZ8"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
def test():
    data = {
        "tema": "matemáticas",
        "nombre": "test libro",
        "link_descarga": "https://example.com",
        "tamaño": 10
    }

    supabase.table("libros").insert(data).execute()

test()
