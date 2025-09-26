import sqlite3

DB = "usuarios.db"

def crear_tabla():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL,
        permisos TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def agregar_usuario():
    usuario = input("👤 Nombre de usuario: ")
    password = input("🔑 Contraseña: ")
    rol = input("🎭 Rol (admin/usuario): ")
    permisos = input("✅ Permisos (ej. NOM_COMPLETO,CICLO_ESCOLAR,ESTATUS_GENERAL o * para todos): ")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO usuarios (usuario, password, rol, permisos) VALUES (?, ?, ?, ?)",
                  (usuario, password, rol, permisos))
        conn.commit()
        print(f"✅ Usuario '{usuario}' agregado correctamente.")
    except sqlite3.IntegrityError:
        print(f"⚠️ El usuario '{usuario}' ya existe.")
    conn.close()

def listar_usuarios():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, usuario, rol, permisos FROM usuarios")
    usuarios = c.fetchall()
    if usuarios:
        print("\n📋 Lista de usuarios:")
        for u in usuarios:
            print(f"ID: {u[0]} | Usuario: {u[1]} | Rol: {u[2]} | Permisos: {u[3]}")
    else:
        print("⚠️ No hay usuarios registrados.")
    conn.close()

def borrar_usuario():
    usuario = input("🗑️ Nombre de usuario a eliminar: ")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM usuarios WHERE usuario = ?", (usuario,))
    conn.commit()
    if c.rowcount > 0:
        print(f"🗑️ Usuario '{usuario}' eliminado.")
    else:
        print(f"⚠️ Usuario '{usuario}' no encontrado.")
    conn.close()

def menu():
    crear_tabla()
    while True:
        print("\n===== 📂 ADMINISTRADOR DE USUARIOS =====")
        print("1. Agregar usuario")
        print("2. Listar usuarios")
        print("3. Borrar usuario")
        print("4. Salir")
        opcion = input("👉 Selecciona una opción: ")

        if opcion == "1":
            agregar_usuario()
        elif opcion == "2":
            listar_usuarios()
        elif opcion == "3":
            borrar_usuario()
        elif opcion == "4":
            print("👋 Saliendo del administrador...")
            break
        else:
            print("⚠️ Opción inválida. Intenta de nuevo.")

if __name__ == "__main__":
    menu()
