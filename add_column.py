import sqlite3

# Nombre de tu base de datos
db_path = "usuarios.db"

def add_column_if_not_exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = [info[1] for info in cursor.fetchall()]

    if "campos_permitidos" not in columns:
        print("Agregando columna 'campos_permitidos'...")
        cursor.execute("ALTER TABLE usuarios ADD COLUMN campos_permitidos TEXT")
        conn.commit()
        print("Columna agregada correctamente ✅")
    else:
        print("La columna 'campos_permitidos' ya existe ✅")

    conn.close()

if __name__ == "__main__":
    add_column_if_not_exists()
