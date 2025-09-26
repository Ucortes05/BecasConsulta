from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = "S050716C@@"  # Cambia esto a una clave fuerte

# --- Función auxiliar para conectar a la base ---
def get_db_connection():
    conn = sqlite3.connect("usuarios.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- Decorador para restringir acceso a administradores ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        rol_sesion = session.get("rol", "").strip().lower()
        if "usuario" not in session or rol_sesion != "admin":
            flash("Acceso no autorizado. Solo administradores.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

# --- Rutas de administración ---
@app.route("/admin")
@admin_required
def admin_panel():
    conn = get_db_connection()
    usuarios = conn.execute("SELECT * FROM usuarios").fetchall()
    conn.close()
    return render_template("admin.html", usuarios=usuarios)

@app.route("/admin/agregar", methods=["POST"])
@admin_required
def agregar_usuario():
    usuario = request.form["usuario"].strip()
    password = request.form["password"].strip()
    rol = request.form["rol"]

    # Recuperar permisos de checkboxes
    campos_permitidos = request.form.getlist("campos_permitidos")

    # Si es admin → guarda None (tiene acceso total)
    if rol == "admin":
        campos_permitidos_str = None
    else:
        campos_permitidos_str = ",".join(campos_permitidos) if campos_permitidos else ""

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO usuarios (usuario, password, rol, campos_permitidos)
        VALUES (?, ?, ?, ?)
    """, (usuario, password, rol, campos_permitidos_str))
    conn.commit()
    conn.close()

    flash("Usuario agregado correctamente.", "success")
    return redirect(url_for("admin_panel"))

# --- Editar usuario ---
@app.route("/editar_usuario/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):
    conn = get_db_connection()
    usuario = conn.execute("SELECT * FROM usuarios WHERE id = ?", (id,)).fetchone()

    if not usuario:
        conn.close()
        return "Usuario no encontrado", 404

    if request.method == "POST":
        nuevo_usuario = request.form["usuario"].strip()
        nueva_password = request.form["password"].strip()
        nuevo_rol = request.form["rol"]

        # Recuperar checkboxes de campos permitidos
        campos_permitidos = request.form.getlist("campos_permitidos")

        # Si es admin → guarda None
        if nuevo_rol == "admin":
            campos_permitidos_str = None
        else:
            campos_permitidos_str = ",".join(campos_permitidos) if campos_permitidos else ""

        # Guardar cambios en la BD
        conn.execute("""
            UPDATE usuarios
            SET usuario = ?, password = ?, rol = ?, campos_permitidos = ?
            WHERE id = ?
        """, (nuevo_usuario, nueva_password, nuevo_rol, campos_permitidos_str, id))
        conn.commit()
        conn.close()

        return redirect(url_for("admin_panel"))

    # Si es GET → mostrar formulario con datos actuales
    usuario_dict = dict(usuario)

    # Convertir campos_permitidos en lista
    if usuario_dict.get("campos_permitidos"):
        campos_seleccionados = usuario_dict["campos_permitidos"].split(",")
    else:
        campos_seleccionados = []

    columnas_disponibles = df.columns.tolist()

    conn.close()
    return render_template(
        "editar_usuario.html",
        usuario=usuario_dict,
        columnas=columnas_disponibles,
        campos_seleccionados=campos_seleccionados
    )


@app.route("/admin/eliminar/<int:id>")
@admin_required
def eliminar_usuario(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM usuarios WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Usuario eliminado.", "danger")
    return redirect(url_for("admin_panel"))

# --- Cargar base de datos de alumnos ---
df = pd.read_excel("alumnos.xlsx")
df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")

# Diccionario de nombres amigables
column_labels = {
    #"CURP": "CURP del Alumno",
    #"NOM_COMPLETO": "Nombre Completo",
    #"CICLO_ESCOLAR": "Ciclo Escolar",
    #"TRAMITE": "Tipo de Trámite",
    #"ESTATUS_GENERAL": "Estatus de la Solicitud",
    #"PLANTEL": "Plantel",
    #"SEDE": "Sede",
    #"CCT": "Clave del Centro de Trabajo",
    #"ESTATUS_REF": "Estatus de Referencia",
    #"FECHA_REF": "Fecha de Referencia",
    #"REFERENCIA": "Número de Referencia",
    #"FILA": "Fila en Base de Datos",
    #"SisAAE": "Sistema AAE"
#-----------------------
    "Orden Nomina": "Orden de la Nomina",
    "Orden referencia": "Orden de la Referencia",
    "Idtramite": "Folio",
    "CURP": "CURP",
    "ESTATUS BECAS": "Estatus de Becas",
    "ESTATUS GENERAL": "Estatus del Alumno",
    "RFC": "RFC",
    "NombreSolicitante": "Nombre del Alumno x Nombre",
    "Nom_Completo": "Nombre del Alumno",
    "FechaSol": "Fecha de Solicitud",
    "FechaCita": "Fecha de Cita",
    "CveApoyo": "Clave de Apoyo",
    "Tramite": "Programa",
    "Monto de Beca": "Monto de Beca",
    "Monto_Letra": "Monto en Letra",
    "Folio": "Folio Exp. Digital",
    "CveDep": "Clave de la Dependencia",
    "Dependencia": "Dependencia",
    "CveProcedencia": "Clave de Procedencia",
    "Procedencia": "Procedencia",
    "CveSubProcedencia": "Clave Sub Procedencia",
    "SubProcedencia": "Sub Procendencia",
    "CveEstatus": "Clave Estatus",
    "Estatus": "Estatus Exp. Digital",
    "CveRazonSocial": "Clave Razon Social",
    "Nombres": "Nombre",
    "ApellidoP": "Primer Apellido",
    "ApellidoM": "Segundo Apellido",
    "Calle": "Calle",
    "No Ext": "N° Ext.",
    "No Int": "N° Int.",
    "Colonia": "Fracc./Col.",
    "CP": "C.P.",
    "Municipio": "Municipio",
    "Teléfono": "Teléfono",
    "Correo": "E-Mail",
    "Solicitud": "Solicitud",
    "Respuesta": "Respuesta Exp. Digital",
    "Fecha Modificado": "Fecha Modificacion",
    "Atendio": "Atendio",
    "Ciclo Escolar": "Ciclo Escolar",
    "CCT": "CCT",
    "Nivel": "Nivel",
    "Plantel": "Plantel",
    "SisAAE": "SisAAE",
    "Mpio Plantel": "Mpio Plantel",
    "Ubicacion Plantel": "Ubicación Plantel",
    "LATITUD": "Latitud",
    "LONGITUD": "Longitud",
    "Turno": "Turno",
    "Grado": "Grado",
    "Grupo": "Grupo",
    "Promedio": "Promedio",
    "CURP Solicitante": "CURP Solicitante",
    "Sexo": "Sexo",
    "Nombre Alumno": "Nombre Alumno",
    "Primer Apellido Alumno": "Primer Apellido Alumno",
    "Segundo Apellido Alumno": "Segundo Apellido Alumno",
    "Fecha Nac Alumno": "Fecha de Nacimiento",
    "Ingreso Familiar": "Ingreso Familiar",
    "Ocupacion": "Ocupacion",
    "CURP Papa": "CURP Papá",
    "Nombre Completo Papa x Nombre": "Nombre Completo Papa x Nombre",
    "Nombre Completo Papa x Apellido": "Nombre Completo Papa x Apellido",
    "Nombre Papa": "Nombre Papa",
    "Primer Apellido Papa": "Primer Apellido Papa",
    "Segundo Apellido Papa": "Segundo Apellido Papa",
    "CURP Mama": "CURP Mama",
    "Nombre Completo Mama x Nombre": "Nombre Completo Mama x Nombre",
    "Nombre Completo Mama x Apellido": "Nombre Completo Mama x Apellido",
    "Nombre Mama": "Nombre Mama",
    "Primer Apellido Mama": "Primer Apellido Mama",
    "Segundo Apellido Mama": "Segundo Apellido Mama",
    "Tarjeta Soluciones": "Tarjeta Soluciones",
    "Dia Evento": "Dia Evento",
    "Nombre_Cobra": "Nombre Quien Cobra",
    "Primer Ap_Cobra": "Nombre Quien Cobra",
    "Segundo Ap_Cobra": "Primer Apellido Quien Cobra",
    "NomComp_Cobra": "Segundo Apellido Quien Cobra",
    "Fila Evento": "Fila evento",
    "Municipio Sede": "Municipio Sede",
    "Fecha de vigencia": "Fecha de vigencia referencia",
    "Referencia": "N° Referencia",
    "1 Estatus Referencia": "Estatus Inicial de Referencia",
    "2 Estaus Referencia": "Estatus 1er Referencia",
    "Fecha_mov": "Fecha de Movimiento",
    "Referencia2": "N° Referencia 2",
    "Estatus Referencia2": "Estatus 2da Referencia",
    "Fecha_Mov2": "Fecha de Movimiento 2",
    "Referencia3": "N° Referencia 3",
    "Estatus Referencia3": "Estatus 3er Referencia",
    "Fecha_Mov3": "Fecha de Movimiento 3",
    "Ref2_Retorna": "N° Referencia 2do Pago",
    "Estatus_Ref2 Retorna": "Estatus 2do pago Referencia",
    "Fecha_Ref2 Retorna": "Fecha de Movimiento 2do Pago",
    "Monto de Beca2": "Monto 2do Pago Beca",
    "Monto_Letra2": "Monto en Letra 2do Pago Beca",
    "Ref_Retorna3": "N° Referencia 2 de 2do Pago",
    "Estatus_Ref Retorna3": "Estatus 2da Referencia",
    "Fecha_Ref3 Retorna": "Fecha de Movimiento 2 de 2do Pago",
    "Tutor": "Nombre Tutor",
    "Estatus Final Referencia": "Estatus Final de Referencia"

    
}

# --- Ruta de login ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        conn = sqlite3.connect("usuarios.db")
        c = conn.cursor()
        # Traer también campos_permitidos
        c.execute("SELECT id, usuario, rol, campos_permitidos FROM usuarios WHERE usuario=? AND password=?", (usuario, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["usuario"] = user[1]
            session["rol"] = user[2]

            # 🔹 Normalizamos campos permitidos
            if user[3]:
                permisos = [col.strip().upper().replace(" ", "_") for col in user[3].split(",")]
                session["campos_permitidos"] = ",".join(permisos)
            else:
                session["campos_permitidos"] = ""

            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")



# --- Ruta para cerrar sesión ---
@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("login"))

# --- Página principal ---
@app.route("/")
def home():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", usuario=session["usuario"])


# --- Buscar alumno ---
@app.route("/buscar", methods=["GET", "POST"])
def buscar_alumno():
    mensaje = None
    resultados = {}

    if request.method == "POST":
        termino = request.form.get("termino", "").lower().strip()

        # Filtrar coincidencias
        mask = (
            df["CURP"].str.lower().str.contains(termino) |
            df["NOM_COMPLETO"].str.lower().str.contains(termino) |
            df["APELLIDOP"].str.lower().str.contains(termino) |
            df["APELLIDOM"].str.lower().str.contains(termino) |
            df["NOMBRES"].str.lower().str.contains(termino)
        )
        resultados_df = df[mask]

        if resultados_df.empty:
            mensaje = "No se encontraron resultados"
        else:
            # Agrupar por CURP
            for curp, grupo in resultados_df.groupby("CURP"):
                resultados[curp] = grupo.to_dict("records")

    # --- Columnas visibles según permisos ---
    todas_columnas = list(df.columns)

    if session.get("rol") == "admin":
        columnas_visibles = todas_columnas
    else:
        permisos = session.get("campos_permitidos", "")
        if permisos:
            columnas_visibles = permisos.split(",")
        else:
            columnas_visibles = ["NOM_COMPLETO", "CICLO_ESCOLAR", "ESTATUS_GENERAL"]

    # Asegurar columnas mínimas
    obligatorias = ["NOM_COMPLETO", "CICLO_ESCOLAR", "ESTATUS_GENERAL"]
    columnas_visibles = list(dict.fromkeys(obligatorias + columnas_visibles))

    labels = {col: column_labels.get(col, col) for col in columnas_visibles}


    return render_template(
        "buscar.html" if not resultados else "lista_alumnos.html",
        mensaje=mensaje,
        resultados=resultados,
        columnas_visibles=columnas_visibles,
        labels=labels
    )




@app.route("/mostrar", methods=["POST"])
def mostrar_resultados():
    curp = request.form.get("curp")
    ciclos = request.form.getlist("ciclos")
    columnas = request.form.getlist("columnas")  # columnas seleccionadas por el usuario

    if not curp:
        return "Error: no se recibió CURP", 400

    # Filtrar registros del alumno
    registros = df[df["CURP"] == curp]
    if ciclos:
        registros = registros[registros["CICLO_ESCOLAR"].isin(ciclos)]
    registros = registros.fillna("No Aplica")


    if registros.empty:
        return render_template(
            "lista_alumnos.html",
            resultados={},
            columnas=df.columns.tolist(),
            termino=curp,
            mensaje="No se encontraron registros",
            labels=labels,
            seleccion_columnas=["NOM_COMPLETO", "CICLO_ESCOLAR", "ESTATUS_GENERAL"],
            usuario_permisos=session.get(
                "campos_permitidos",
                ["NOM_COMPLETO", "CICLO_ESCOLAR", "ESTATUS_GENERAL"]
            )
        )

    # --- Permisos del usuario ---
    if session.get("rol") == "admin":
        permisos_usuario = df.columns.tolist()
    else:
        permisos_usuario = session.get("campos_permitidos", "")
        if permisos_usuario:
            permisos_usuario = [col.strip().upper().replace(" ", "_") for col in permisos_usuario.split(",")]
        else:
            permisos_usuario = ["NOM_COMPLETO", "CICLO_ESCOLAR", "ESTATUS_GENERAL"]

    # Normalizar columnas seleccionadas
    columnas = [col.strip().upper().replace(" ", "_") for col in columnas]

    # Si no se seleccionaron columnas, usamos las obligatorias
    if not columnas:
        columnas_validas = ["NOM_COMPLETO", "CICLO_ESCOLAR", "ESTATUS_GENERAL"]
    else:
        # Filtrar columnas seleccionadas según permisos del usuario
        columnas_validas = [col for col in columnas if col in permisos_usuario]

    # 🔍 Debug en consola
    print("Columnas seleccionadas:", columnas)
    print("Columnas válidas (permitidas + seleccionadas):", columnas_validas)

    # Mandar todos los registros completos, pero en la vista solo se mostrarán columnas_validas
    registros_dict = registros.to_dict(orient="records")

    # Normalizar claves a mayúsculas para coincidir con DataFrame
    registros_dict = [{k.upper(): v for k, v in row.items()} for row in registros_dict]

    # Asegurarse que columnas_validas también están en mayúsculas
    columnas_validas = [col.upper() for col in columnas_validas]

    labels = {col: column_labels.get(col, col) for col in columnas_validas}


    return render_template(
        "resultados.html",
        registros=registros_dict,
        columnas=columnas_validas,
        alumno=registros.iloc[0]["NOM_COMPLETO"],
        labels=labels
    )




# --- Ruta salir ---
@app.route("/salir")
def salir():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

