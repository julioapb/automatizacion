from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.config.from_pyfile("config.py")

mysql = MySQL(app)


# ========== RUTAS DE AUTENTICACIÓN ==========
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM usuarios WHERE usuario=%s AND password=%s", (usuario, password))
        user = cursor.fetchone()

        if user:
            session["loggedin"] = True
            session["usuario"] = user["usuario"]
            return redirect(url_for("panel"))
        else:
            flash("Usuario o contraseña incorrectos", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ========== PANEL ==========
@app.route("/panel")
def panel():
    if not session.get("loggedin"):
        return redirect(url_for("login"))
    return render_template("panel.html", usuario=session["usuario"])


# ========== FORMULARIO ==========
@app.route("/formulario", methods=["GET", "POST"])
def formulario():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO registros (nombre, email) VALUES (%s, %s)", (nombre, email))
        mysql.connection.commit()

        flash("Datos guardados correctamente", "success")
        return redirect(url_for("tabla"))

    return render_template("formulario.html")


# ========== TABLA ==========
@app.route("/tabla")
def tabla():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM pedidos")
    datos = cursor.fetchall()

    return render_template("tabla.html", datos=datos)


# ========= Crear Cliente ========

@app.route("/cliente", methods=["GET", "POST"])
def cliente():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        no_documento = request.form.get("no_documento")
        direccion = request.form.get("direccion")
        ciudad = request.form.get("ciudad")
        cp = request.form.get("cp")
        telefono = request.form.get("telefono")
        correo = request.form.get("correo")

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO cliente (nombre, no_documento, direccion, ciudad, cp, telefono, correo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, no_documento, direccion, ciudad, cp, telefono, correo))
        mysql.connection.commit()

        flash("Cliente registrado correctamente", "success")
        return redirect(url_for("panel"))   # o redirige donde quieras

    return render_template("cliente.html")

# ====== Clientes 

@app.route("/clientes")
def clientes():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM cliente")
    lista_clientes = cursor.fetchall()

    return render_template("clientes.html", clientes=lista_clientes)



@app.route("/cliente/editar/<int:id_cliente>", methods=["GET", "POST"])
def editar_cliente(id_cliente):
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        nombre = request.form.get("nombre")
        no_documento = request.form.get("no_documento")
        direccion = request.form.get("direccion")
        ciudad = request.form.get("ciudad")
        cp = request.form.get("cp")
        telefono = request.form.get("telefono")
        correo = request.form.get("correo")

        cursor.execute("""
            UPDATE cliente
            SET nombre=%s, no_documento=%s, direccion=%s, ciudad=%s, cp=%s, telefono=%s, correo=%s
            WHERE id_cliente=%s
        """, (nombre, no_documento, direccion, ciudad, cp, telefono, correo, id_cliente))
        mysql.connection.commit()

        flash("Cliente actualizado correctamente ✅", "success")
        return redirect(url_for("clientes"))

    # Si es GET, obtenemos los datos para mostrar en el formulario
    cursor.execute("SELECT * FROM cliente WHERE id_cliente=%s", (id_cliente,))
    cliente = cursor.fetchone()

    return render_template("editar_cliente.html", cliente=cliente)

@app.route("/cliente/eliminar/<int:id_cliente>")
def eliminar_cliente(id_cliente):
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,))
    mysql.connection.commit()

    flash("Cliente eliminado correctamente 🗑️", "success")
    return redirect(url_for("clientes"))


if __name__ == "__main__":
    app.run(debug=True)