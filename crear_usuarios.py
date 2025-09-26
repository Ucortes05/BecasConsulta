import sqlite3

# Nombre de la base de datos
db_name = "usuarios.db"

# Conectar a la base (se crea si no existe)
conn = sqlite3.connect(db_name)
c = conn.cursor()

# 1. Eliminar tabla si ya existía (para reiniciar desde cero)
c.execute("DROP TABLE IF EXISTS usuarios")

# 2. Crear la tabla de usuarios
c.execute("""
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    contrasena TEXT NOT NULL,
    rol TEXT NOT NULL
)
""")

# 3. Insertar usuarios de ejemplo
usuarios = [
    ("admin", "1234", "admin"),
    ("ulises", "abcd", "lector"),
    ("juan", "5678", "lector")
]

c.executemany("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)", usuarios)

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()

print(f"✅ Base de datos '{db_name}' creada con usuarios de ejemplo.")
