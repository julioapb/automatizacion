from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.config.from_pyfile("config.py")

# ===== Función de conexión =====
def get_db_connection():
    return mysql.connector.connect(
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DB"],
        port=app.config["MYSQL_PORT"]
    )

# ========== LOGIN ==========
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario=%s AND password=%s", (usuario, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

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



# ========= CREAR CLIENTE ========
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

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cliente (nombre, no_documento, direccion, ciudad, cp, telefono, correo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, no_documento, direccion, ciudad, cp, telefono, correo))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Cliente registrado correctamente ✅", "success")
        return redirect(url_for("clientes"))

    return render_template("cliente.html")

# ====== LISTAR CLIENTES ======
@app.route("/clientes")
def clientes():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cliente")
    lista_clientes = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("clientes.html", clientes=lista_clientes)

# ====== EDITAR CLIENTE ======
@app.route("/cliente/editar/<int:id_cliente>", methods=["GET", "POST"])
def editar_cliente(id_cliente):
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

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
        conn.commit()
        cursor.close()
        conn.close()

        flash("Cliente actualizado correctamente ✅", "success")
        return redirect(url_for("clientes"))

    cursor.execute("SELECT * FROM cliente WHERE id_cliente=%s", (id_cliente,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("editar_cliente.html", cliente=cliente)

# ====== ELIMINAR CLIENTE ======
@app.route("/cliente/eliminar/<int:id_cliente>")
def eliminar_cliente(id_cliente):
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Verificar si hay pedidos asociados
    cursor.execute("SELECT COUNT(*) AS total FROM pedidos WHERE id_cliente=%s", (id_cliente,))
    total = cursor.fetchone()["total"]

    if total > 0:
        flash("❌ No se puede eliminar el cliente, tiene pedidos asociados.", "danger")
    else:
        cursor.close()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cliente WHERE id_cliente=%s", (id_cliente,))
        conn.commit()
        flash("Cliente eliminado correctamente 🗑️", "success")

    cursor.close()
    conn.close()
    return redirect(url_for("clientes"))

# ========= CREAR PEDIDO ========
@app.route("/pedido/nuevo", methods=["GET", "POST"])
def nuevo_pedido():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Listar clientes, colores y servicios
    cursor.execute("SELECT id_cliente, nombre FROM cliente")
    clientes = cursor.fetchall()

    cursor.execute("SELECT id_color, nombre_color FROM color")
    colores = cursor.fetchall()

    cursor.execute("SELECT id_servicio, descripcion FROM servicio")
    servicios = cursor.fetchall()

    if request.method == "POST":
        numero_pedido = request.form.get("numero_pedido")
        id_cliente = request.form.get("id_cliente")
        fecha_pedido = request.form.get("fecha_pedido")
        fecha_entrega = request.form.get("fecha_entrega")
        usuario = session["usuario"]

        # Insertar pedido general
        cursor.close()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pedidos (numero_pedido, id_cliente, fecha_pedido, fecha_entrega, usuario)
            VALUES (%s, %s, %s, %s, %s)
        """, (numero_pedido, id_cliente, fecha_pedido, fecha_entrega, usuario))
        conn.commit()
        id_pedido = cursor.lastrowid

        # Insertar servicios asociados
        servicios_ids = request.form.getlist("id_servicio[]")
        colores_ids = request.form.getlist("id_color[]")
        cantidades = request.form.getlist("cantidad[]")
        precios = request.form.getlist("precio_unitario[]")
        descuentos = request.form.getlist("descuento[]")
        fechas_recepcion = request.form.getlist("fecha_recepcion[]")

        for i in range(len(servicios_ids)):
            cursor.execute("""
                INSERT INTO pedido_servicio
                (id_pedido, id_servicio, id_color, cantidad, precio_unitario, descuento, fecha_recepcion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                id_pedido,
                servicios_ids[i],
                colores_ids[i],
                cantidades[i],
                precios[i],
                descuentos[i] if descuentos[i] else 0,
                fechas_recepcion[i]
            ))
        conn.commit()

        cursor.close()
        conn.close()

        flash("Pedido registrado correctamente ✅", "success")
        return redirect(url_for("pedidos"))

    cursor.close()
    conn.close()
    return render_template("pedido_form.html", clientes=clientes, colores=colores, servicios=servicios)



# ========== LISTAR PEDIDOS ==========
@app.route("/pedidos")
def pedidos():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.id_pedido, p.numero_pedido, c.nombre AS cliente,
               p.fecha_pedido, p.fecha_entrega, p.usuario,
               s.descripcion AS servicio, col.nombre_color AS color,
               ps.cantidad, ps.precio_unitario, ps.descuento, ps.neto, ps.fecha_recepcion
        FROM pedidos p
        JOIN cliente c ON p.id_cliente = c.id_cliente
        LEFT JOIN pedido_servicio ps ON p.id_pedido = ps.id_pedido
        LEFT JOIN servicio s ON ps.id_servicio = s.id_servicio
        LEFT JOIN color col ON ps.id_color = col.id_color
        ORDER BY p.fecha_pedido DESC, p.id_pedido DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    pedidos_dict = {}
    for row in rows:
        id_pedido = row["id_pedido"]
        if id_pedido not in pedidos_dict:
            pedidos_dict[id_pedido] = {
                "id_pedido": id_pedido,
                "numero_pedido": row["numero_pedido"],
                "cliente": row["cliente"],
                "fecha_pedido": row["fecha_pedido"],
                "fecha_entrega": row["fecha_entrega"],
                "usuario": row["usuario"],
                "servicios": []
            }
        if row["servicio"]:
            pedidos_dict[id_pedido]["servicios"].append({
                "servicio": row["servicio"],
                "color": row["color"],
                "cantidad": row["cantidad"],
                "precio_unitario": row["precio_unitario"],
                "descuento": row["descuento"],
                "neto": row["neto"],
                "fecha_recepcion": row["fecha_recepcion"]
            })

    return render_template("pedidos.html", pedidos=pedidos_dict.values())




# ========= CREAR COLOR ========
@app.route("/color/nuevo", methods=["GET", "POST"])
def nuevo_color():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    if request.method == "POST":
        codigo = request.form.get("codigo_color")
        nombre = request.form.get("nombre_color")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO color (codigo_color, nombre_color) VALUES (%s, %s)",
            (codigo, nombre)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Color agregado correctamente ✅", "success")
        return redirect(url_for("colores"))

    return render_template("color_form.html")


@app.route("/colores")
def colores():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM color ORDER BY id_color DESC")
    lista_colores = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("colores.html", colores=lista_colores)

@app.route("/servicios")
def servicios():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM servicio ORDER BY id_servicio DESC")
    lista_servicios = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("servicios.html", servicios=lista_servicios)

# ========= CREAR SERVICIO ========
@app.route("/servicio/nuevo", methods=["GET", "POST"])
def nuevo_servicio():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    if request.method == "POST":
        referencia = request.form.get("referencia")
        descripcion = request.form.get("descripcion")
        precio = request.form.get("precio")

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO servicio (referencia, descripcion, precio)
                VALUES (%s, %s, %s)
            """, (referencia, descripcion, precio))
            conn.commit()
            flash("Servicio agregado correctamente ✅", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error: {str(e)}", "danger")

        cursor.close()
        conn.close()
        return redirect(url_for("servicios"))

    return render_template("servicio_form.html")

@app.route("/servicio/editar/<int:id_servicio>", methods=["GET", "POST"])
def editar_servicio(id_servicio):
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        referencia = request.form.get("referencia")
        descripcion = request.form.get("descripcion")
        precio = request.form.get("precio")

        try:
            cursor.close()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE servicio
                SET referencia=%s, descripcion=%s, precio=%s
                WHERE id_servicio=%s
            """, (referencia, descripcion, precio, id_servicio))
            conn.commit()
            flash("Servicio actualizado correctamente ✅", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error: {str(e)}", "danger")

        cursor.close()
        conn.close()
        return redirect(url_for("servicios"))

    cursor.execute("SELECT * FROM servicio WHERE id_servicio=%s", (id_servicio,))
    servicio = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("editar_servicio.html", servicio=servicio)


if __name__ == "__main__":
    app.run(debug=True)



