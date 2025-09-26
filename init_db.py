import sqlite3

# Conectar o crear el archivo usuarios.db
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    contrasena TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('admin','lector'))
)
""")

# Revisar si ya hay usuarios
cursor.execute("SELECT COUNT(*) FROM usuarios")
count = cursor.fetchone()[0]

# Si no hay usuarios, insertamos uno por defecto
if count == 0:
    cursor.execute("""
    INSERT INTO usuarios (usuario, contrasena, rol)
    VALUES (?, ?, ?)
    """, ("admin", "admin123", "admin"))
    print("✅ Usuario admin creado: usuario='admin', contraseña='admin123'")
else:
    print("ℹ️ Ya existen usuarios en la tabla, no se insertó nada.")

conn.commit()
conn.close()
