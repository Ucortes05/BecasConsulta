import sqlite3

DB_NAME = "usuarios.db"

def migrate_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Verificar columnas actuales
    c.execute("PRAGMA table_info(usuarios)")
    columnas = [col[1] for col in c.fetchall()]
    print("Columnas actuales:", columnas)

    if "contrasena" not in columnas:
        print("La columna 'contraseña' no existe. No se requiere migración.")
        conn.close()
        return

    # 1. Renombrar la tabla actual
    c.execute("ALTER TABLE usuarios RENAME TO usuarios_old")

    # 2. Crear la nueva tabla con 'password'
    c.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    """)

    # 3. Copiar datos de la tabla vieja a la nueva
    c.execute("INSERT INTO usuarios (id, usuario, password, rol) SELECT id, usuario, contrasena, rol FROM usuarios_old")

    # 4. Eliminar la tabla vieja
    c.execute("DROP TABLE usuarios_old")

    conn.commit()
    conn.close()
    print("Migración completada: 'contrasena' → 'password'")

if __name__ == "__main__":
    migrate_db()
