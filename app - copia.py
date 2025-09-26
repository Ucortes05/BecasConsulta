from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Cargar base de datos
df = pd.read_excel("alumnos.xlsx")
df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")

# Portada
@app.route("/")
def home():
    return render_template("home.html")

# Formulario de búsqueda
@app.route("/buscar", methods=["GET", "POST"])
def buscar_alumno():
    if request.method == "POST":
        termino = request.form.get("termino", "").strip()
        if not termino:
            return render_template("buscar.html", mensaje="Escribe un nombre o CURP")

        # Buscar coincidencias en todo el DataFrame
        resultados = df[df.apply(
            lambda row: row.astype(str).str.contains(termino, case=False, na=False).any(), axis=1
        )]

        if resultados.empty:
            return render_template("no_encontrado.html", termino=termino)

        # Agrupar por CURP
        alumnos = {}
        for curp, grupo in resultados.groupby("CURP"):
            alumnos[curp] = grupo.to_dict(orient="records")

        return render_template("lista_alumnos.html", resultados=alumnos, columnas=df.columns, termino=termino)

    return render_template("buscar.html")

# Mostrar resultados seleccionados
@app.route("/mostrar", methods=["POST"])
def mostrar_resultados():
    seleccion = request.form
    curp = seleccion.get("curp")
    if not curp:
        return "Error: No se recibió CURP", 400

    # Obtener ciclos seleccionados
    ciclos = seleccion.getlist("ciclos")
    if not ciclos:
        ciclos = df[df["CURP"] == curp]["CICLO_ESCOLAR"].unique().tolist()

    # Columnas seleccionadas
    campos = seleccion.getlist("columnas")
    if "CURP" not in campos:
        campos.insert(0, "CURP")
    if "NOM_COMPLETO" not in campos:
        campos.insert(1, "NOM_COMPLETO")

    # Filtrar registros
    registros = df[(df["CURP"] == curp) & (df["CICLO_ESCOLAR"].isin(ciclos))]
    if registros.empty:
        mensaje = "No se encontraron registros para el alumno y ciclos seleccionados."
        return render_template("lista_alumnos.html", resultados={}, columnas=campos, mensaje=mensaje, termino=curp)

    registros = registros.fillna("No Aplica")
    registros_dict = registros.to_dict(orient="records")

    # Ordenar resultados alfabéticamente por nombre
    resultados = {curp: registros_dict}  # para un solo alumno, si hay varios, agrupar según tu lógica
    resultados_ordenados = dict(sorted(resultados.items(), key=lambda item: item[1][0]["NOM_COMPLETO"]))

    return render_template(
        "lista_alumnos.html",
        resultados=resultados_ordenados,
        columnas=campos,
        termino=registros_dict[0]["NOM_COMPLETO"]
    )


if __name__ == "__main__":
    app.run(debug=True)
