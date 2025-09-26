import sqlite3

# Conectar a la base de datos de usuarios
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

# Ver la estructura de la tabla
print("=== Columnas de la tabla usuarios ===")
cursor.execute("PRAGMA table_info(usuarios);")
for col in cursor.fetchall():
    print(col)

# Consultar todos los usuarios y sus permisos
print("\n=== Usuarios registrados ===")
cursor.execute("SELECT id, usuario, rol, campos_permitidos FROM usuarios;")
rows = cursor.fetchall()

if rows:
    for row in rows:
        print(f"ID: {row[0]} | Usuario: {row[1]} | Rol: {row[2]} | Permisos: {row[3]}")
else:
    print("No hay usuarios registrados en la tabla.")

conn.close()
