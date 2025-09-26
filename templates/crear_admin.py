import sqlite3

conn = sqlite3.connect("usuarios.db")
conn.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
             ("admin", "1234", "admin"))
conn.commit()
conn.close()
print("Usuario admin creado")
