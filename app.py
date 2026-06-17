from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from datetime import datetime
from io import BytesIO
from reportlab.lib.colors import HexColor
from datetime import date
from werkzeug.utils import secure_filename
import os
import mysql.connector
import math
import io


app = Flask(__name__)
app.config.from_pyfile("config.py")

# Carpeta de subida y tipos permitidos
UPLOAD_FOLDER = os.path.join('static', 'img', 'servicios')
ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg')


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ===== Función para validar extensión =====
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===== Funciones auxiliares =====
def buscar_imagen_servicio(ref, id_cliente):
    base_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{ref}_{id_cliente}")
    for extension in ALLOWED_EXTENSIONS:
        ruta_imagen = f"{base_path}.{extension}"
        if os.path.exists(ruta_imagen):
            return ruta_imagen
    return None

# ===== Función de conexión =====
def get_db_connection():
    return mysql.connector.connect(
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DB"],
        port=app.config["MYSQL_PORT"]
    )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    return render_template("pedido_form.html", clientes=clientes, colores=colores, servicios=servicios, fecha_hoy = date.today().strftime("%Y-%m-%d"))


@app.route("/pedido/editar/<int:id_pedido>", methods=["GET", "POST"])
def editar_pedido(id_pedido):
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id_cliente, nombre FROM cliente")
    clientes = cursor.fetchall()

    cursor.execute("SELECT id_color, nombre_color FROM color")
    colores = cursor.fetchall()

    cursor.execute("SELECT id_servicio, referencia, descripcion FROM servicio ORDER BY referencia")
    servicios = cursor.fetchall()

    if request.method == "POST":
        numero_pedido = request.form.get("numero_pedido")
        id_cliente = request.form.get("id_cliente")
        fecha_pedido = request.form.get("fecha_pedido")
        fecha_entrega = request.form.get("fecha_entrega")

        ids_detalle = request.form.getlist("id_pedido_servicio[]")
        servicios_ids = request.form.getlist("id_servicio[]")
        colores_ids = request.form.getlist("id_color[]")
        cantidades = request.form.getlist("cantidad[]")
        precios = request.form.getlist("precio_unitario[]")
        descuentos = request.form.getlist("descuento[]")
        fechas_recepcion = request.form.getlist("fecha_recepcion[]")

        try:
            cursor.close()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                UPDATE pedidos
                SET numero_pedido=%s, id_cliente=%s, fecha_pedido=%s, fecha_entrega=%s
                WHERE id_pedido=%s
            """, (numero_pedido, id_cliente, fecha_pedido, fecha_entrega, id_pedido))

            cursor.execute(
                "SELECT id_pedido_servicio FROM pedido_servicio WHERE id_pedido=%s",
                (id_pedido,)
            )
            existentes = {str(row["id_pedido_servicio"]) for row in cursor.fetchall()}
            enviados = {detalle_id for detalle_id in ids_detalle if detalle_id}

            for detalle_id in existentes - enviados:
                cursor.execute(
                    "DELETE FROM pedido_servicio WHERE id_pedido_servicio=%s AND id_pedido=%s",
                    (detalle_id, id_pedido)
                )

            for i, id_servicio in enumerate(servicios_ids):
                if not id_servicio:
                    continue

                detalle_id = ids_detalle[i] if i < len(ids_detalle) else ""
                id_color = colores_ids[i] if i < len(colores_ids) else None
                cantidad = cantidades[i] if i < len(cantidades) else 0
                precio = precios[i] if i < len(precios) else 0
                descuento = descuentos[i] if i < len(descuentos) and descuentos[i] else 0
                fecha_recepcion = fechas_recepcion[i] if i < len(fechas_recepcion) else fecha_pedido

                if detalle_id:
                    cursor.execute("""
                        UPDATE pedido_servicio
                        SET id_servicio=%s,
                            id_color=%s,
                            cantidad=%s,
                            precio_unitario=%s,
                            descuento=%s,
                            fecha_recepcion=%s
                        WHERE id_pedido_servicio=%s AND id_pedido=%s
                    """, (
                        id_servicio,
                        id_color,
                        cantidad,
                        precio,
                        descuento,
                        fecha_recepcion,
                        detalle_id,
                        id_pedido
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO pedido_servicio
                        (id_pedido, id_servicio, id_color, cantidad, precio_unitario, descuento, fecha_recepcion)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        id_pedido,
                        id_servicio,
                        id_color,
                        cantidad,
                        precio,
                        descuento,
                        fecha_recepcion
                    ))

            conn.commit()
            flash("Pedido actualizado correctamente", "success")
            cursor.close()
            conn.close()
            return redirect(url_for("pedidos"))

        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"No se pudo actualizar el pedido: {str(e)}", "danger")
            return redirect(url_for("editar_pedido", id_pedido=id_pedido))

    cursor.execute("SELECT * FROM pedidos WHERE id_pedido=%s", (id_pedido,))
    pedido = cursor.fetchone()

    if not pedido:
        cursor.close()
        conn.close()
        flash("Pedido no encontrado", "warning")
        return redirect(url_for("pedidos"))

    cursor.execute("""
        SELECT *
        FROM pedido_servicio
        WHERE id_pedido=%s
        ORDER BY id_pedido_servicio
    """, (id_pedido,))
    detalles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "editar_pedido.html",
        pedido=pedido,
        detalles=detalles,
        clientes=clientes,
        colores=colores,
        servicios=servicios,
        fecha_hoy=date.today().strftime("%Y-%m-%d")
    )


@app.route("/pedido/eliminar/<int:id_pedido>")
def eliminar_pedido(id_pedido):
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM pedido_servicio WHERE id_pedido=%s", (id_pedido,))
        cursor.execute("DELETE FROM pedidos WHERE id_pedido=%s", (id_pedido,))
        conn.commit()
        flash("Pedido eliminado correctamente", "success")
    except Exception as e:
        conn.rollback()
        flash(f"No se pudo eliminar el pedido: {str(e)}", "danger")

    cursor.close()
    conn.close()
    return redirect(url_for("pedidos"))



# ========== LISTAR PEDIDOS ==========
@app.route("/pedidos")
def pedidos():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Consulta con el ID real del pedido_servicio
    cursor.execute("""
        SELECT 
            p.id_pedido,
            p.numero_pedido,
            c.nombre AS cliente,
            p.fecha_pedido,
            p.fecha_entrega,
            p.usuario,
            ps.id_pedido_servicio,              -- 👈 ID real del detalle
            s.descripcion AS servicio,
            s.articulos_por_caja,
            col.nombre_color AS color,
            ps.cantidad,
            ps.precio_unitario,
            ps.descuento,
            ps.neto,
            ps.fecha_recepcion,
            CASE 
                WHEN s.articulos_por_caja > 0 THEN CEIL(ps.cantidad / s.articulos_por_caja)
                ELSE 0
            END AS cajas_necesarias
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

    # Agrupar pedidos
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
                "id_pedido_servicio": row["id_pedido_servicio"],  # 👈 necesario para AJAX
                "servicio": row["servicio"],
                "color": row["color"],
                "cantidad": row["cantidad"],
                "precio_unitario": row["precio_unitario"],
                "descuento": row["descuento"],
                "neto": row["neto"],
                "fecha_recepcion": row["fecha_recepcion"],
                "articulos_por_caja": row["articulos_por_caja"],
                "cajas_necesarias": row["cajas_necesarias"]
            })

    return render_template("pedidos.html", pedidos=pedidos_dict.values())




from flask import send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from io import BytesIO
from datetime import date
import math
import os

from flask import send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from io import BytesIO
from datetime import date
import math
import os


# ===== Generar etiqueta ======
@app.route("/etiqueta/<int:id_pedido>")
def generar_etiqueta(id_pedido):
    """Genera etiquetas en PDF para impresión térmica (80x50 mm)."""

    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            p.numero_pedido,
            p.id_cliente,                
            c.nombre AS cliente,
            s.referencia,
            s.articulos_por_caja,
            ps.cantidad,
            col.nombre_color AS color,
            col.codigo_html AS codigo_html
        FROM pedidos p
        JOIN cliente c ON p.id_cliente = c.id_cliente
        JOIN pedido_servicio ps ON p.id_pedido = ps.id_pedido
        JOIN servicio s ON ps.id_servicio = s.id_servicio AND s.id_cliente = p.id_cliente
        LEFT JOIN color col ON ps.id_color = col.id_color
        WHERE p.id_pedido = %s
        """, (id_pedido,))
    registros = cursor.fetchall()
    cursor.close()
    conn.close()

    if not registros:
        flash("No se encontraron servicios para este pedido.", "warning")
        return redirect(url_for("pedidos"))

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(80 * mm, 50 * mm))

    for r in registros:

        # === DATOS DEL SERVICIO (FIJOS PARA ESTE BLOQUE) ===
        ref = r["referencia"]
        color = r["color"] or "-"
        color_html = r["codigo_html"] or "#FFFFFF"
        cantidad = int(r["cantidad"])
        num_pedido = r["numero_pedido"]
        por_caja = r["articulos_por_caja"] or 1
        id_cliente = r["id_cliente"]

        ruta_imagen = buscar_imagen_servicio(ref, id_cliente)

        num_cajas = math.ceil(cantidad / por_caja)
        resto = cantidad % por_caja

        # === ETIQUETAS POR CAJA (DE ESTE SERVICIO) ===
        for i in range(num_cajas):

            cantidad_caja = (
                resto if (i == num_cajas - 1 and resto != 0) else por_caja
            )

            # ===== DIBUJAR ETIQUETA =====
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawCentredString(40 * mm, 42 * mm, ref)

            # Imagen
            if ruta_imagen:
                img = ImageReader(ruta_imagen)
                pdf.drawImage(img, 5 * mm, 10 * mm, width=30 * mm, height=28 * mm)
            else:
                pdf.setFont("Helvetica-Oblique", 8)
                pdf.drawCentredString(20 * mm, 24 * mm, "(Sin imagen)")

            # Datos
            pdf.setFont("Helvetica", 9)
            pdf.drawString(40 * mm, 30 * mm, f"CANTIDAD: {cantidad_caja}")
            pdf.drawString(40 * mm, 22 * mm, f"ORD: {num_pedido}")
            pdf.drawString(40 * mm, 14 * mm, f"COLOR: {color}")

            # Círculo color
            try:
                pdf.setFillColor(HexColor(color_html))
                pdf.circle(45 * mm, 10 * mm, 6, fill=1)
                pdf.setFillColorRGB(0, 0, 0)
            except:
                pass

            pdf.showPage()

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=False,
        download_name=f"etiquetas_pedido_{id_pedido}.pdf",
        mimetype="application/pdf"
    )





# ========= CREAR COLOR ========
@app.route("/color/nuevo", methods=["GET", "POST"])
def nuevo_color():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    if request.method == "POST":
        codigo_cliente = request.form.get("codigo_color")   # código del cliente
        codigo_html = request.form.get("codigo_html")       # código HTML
        nombre = request.form.get("nombre_color")           # nombre del color

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO color (codigo_color, codigo_html, nombre_color)
            VALUES (%s, %s, %s)
        """, (codigo_cliente, codigo_html, nombre))
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

    referencia = request.args.get("referencia", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 20

    if page < 1:
        page = 1

    where_sql = ""
    params = []

    if referencia:
        where_sql = "WHERE s.referencia LIKE %s"
        params.append(f"%{referencia}%")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(f"""
        SELECT COUNT(*) AS total
        FROM servicio s
        {where_sql}
    """, params)
    total_servicios = cursor.fetchone()["total"]
    total_pages = max(1, math.ceil(total_servicios / per_page))

    if page > total_pages:
        page = total_pages

    offset = (page - 1) * per_page

    cursor.execute(f"""
        SELECT s.*, c.nombre AS cliente
        FROM servicio s
        LEFT JOIN cliente c ON s.id_cliente = c.id_cliente
        {where_sql}
        ORDER BY s.id_servicio DESC
        LIMIT %s OFFSET %s
    """, params + [per_page, offset])

    lista_servicios = cursor.fetchall()
    cursor.close()
    conn.close()

    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)
    pages = range(start_page, end_page + 1)

    return render_template(
        "servicios.html",
        servicios=lista_servicios,
        referencia_busqueda=referencia,
        page=page,
        pages=pages,
        first_page_visible=start_page,
        last_page_visible=end_page,
        total_pages=total_pages,
        total_servicios=total_servicios
    )


@app.route("/color/eliminar/<int:id_color>")
def eliminar_color(id_color):
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM color WHERE id_color = %s", (id_color,))
        conn.commit()

        flash("Color eliminado correctamente 🗑️", "success")

    except mysql.connector.Error as err:
        flash(f"No se puede eliminar el color porque está en uso en pedidos. ({err})", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("colores"))


# ========= CREAR SERVICIO ========
@app.route("/servicio/nuevo", methods=["GET", "POST"])
def nuevo_servicio():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id_cliente, nombre FROM cliente")
    clientes = cursor.fetchall()

    if request.method == "POST":
        referencia = request.form.get("referencia").strip()
        descripcion = request.form.get("descripcion")
        precio = request.form.get("precio")
        articulos_por_caja = request.form.get("articulos_por_caja")
        id_cliente = request.form.get("id_cliente")

        imagen = request.files.get("imagen")  # 👈 AQUÍ ESTABA EL FALLO

        try:
            # 1️⃣ Insertar servicio
            cursor.close()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO servicio (referencia, descripcion, precio, articulos_por_caja, id_cliente)
                VALUES (%s, %s, %s, %s, %s)
            """, (referencia, descripcion, precio, articulos_por_caja, id_cliente))
            conn.commit()

            # 2️⃣ Guardar imagen si existe
            if imagen and imagen.filename != "" and allowed_file(imagen.filename):
                extension = imagen.filename.rsplit('.', 1)[1].lower()
                filename = f"{referencia}_{id_cliente}.{extension}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                imagen.save(filepath)

            flash("Servicio agregado correctamente ✅", "success")

        except Exception as e:
            conn.rollback()
            flash(f"Error al crear el servicio: {str(e)}", "danger")

        cursor.close()
        conn.close()
        return redirect(url_for("servicios"))

    cursor.close()
    conn.close()
    return render_template("servicio_form.html", clientes=clientes)



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
        articulos_por_caja = request.form.get("articulos_por_caja")

        try:
            cursor.close()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE servicio
                SET referencia=%s, descripcion=%s, precio=%s, articulos_por_caja=%s
                WHERE id_servicio=%s
            """, (referencia, descripcion, precio, articulos_por_caja, id_servicio))
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

@app.route("/servicio/eliminar/<int:id_servicio>")
def eliminar_servicio(id_servicio):
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM servicio WHERE id_servicio=%s", (id_servicio,))
        conn.commit()
        flash("Servicio eliminado correctamente 🗑️", "success")
    except Exception as e:
        conn.rollback()
        flash(f"No se pudo eliminar: {str(e)}", "danger")

    cursor.close()
    conn.close()
    return redirect(url_for("servicios"))

# ========= ACTUALIZAR SERVICIO (AJAX desde pedidos.html) =========
@app.route("/actualizar_servicio_ajax", methods=["POST"])
def actualizar_servicio_ajax():
    data = request.get_json()
    print("📩 Datos recibidos AJAX:", data)

    id_servicio = data.get("id_servicio")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar nombre de la columna (ajústalo si es distinto)
        sql = """
            UPDATE pedido_servicio
            SET cantidad=%s,
                precio_unitario=%s,
                descuento=%s,
                fecha_recepcion=%s
            WHERE id_pedido_servicio=%s
        """

        valores = (
            data.get("cantidad"),
            data.get("precio_unitario"),
            data.get("descuento"),
            data.get("fecha_recepcion"),
            id_servicio
        )

        print("📦 Ejecutando SQL:", sql)
        print("🔢 Valores:", valores)

        cursor.execute(sql, valores)
        conn.commit()

        filas_afectadas = cursor.rowcount
        print(f"✅ Filas actualizadas: {filas_afectadas}")

        cursor.close()
        conn.close()

        if filas_afectadas == 0:
            return jsonify(success=False, message="No se actualizó ninguna fila (ID incorrecto)")

        return jsonify(success=True)

    except Exception as e:
        print("❌ Error al actualizar servicio AJAX:", e)
        return jsonify(success=False, message=str(e))

#Subir imagenes
@app.route("/subir_imagen", methods=["GET", "POST"])
def subir_imagen():
    if not session.get("loggedin"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            s.id_servicio,
            s.referencia,
            s.descripcion,
            s.id_cliente,
            c.nombre AS cliente
        FROM servicio s
        LEFT JOIN cliente c ON s.id_cliente = c.id_cliente
        ORDER BY c.nombre, s.referencia
    """)
    servicios = cursor.fetchall()
    cursor.close()
    conn.close()

    if request.method == "POST":
        if 'imagen' not in request.files:
            flash("No se seleccionó ningún archivo", "warning")
            return redirect(request.url)
        
        file = request.files['imagen']
        pieza = request.form.get("pieza", "").strip()
        referencia, id_cliente = pieza.split("|", 1) if "|" in pieza else ("", "")

        if file.filename == '':
            flash("Archivo no seleccionado", "danger")
            return redirect(request.url)

        if not referencia or not id_cliente:
            flash("Debes seleccionar la pieza", "warning")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            extension = filename.rsplit('.', 1)[1].lower()

            filename = f"{referencia}_{id_cliente}.{extension}"

            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            flash("Imagen subida correctamente ✅", "success")
            return redirect(url_for("subir_imagen"))

        flash("Formato de archivo no permitido ❌", "danger")
        return redirect(request.url)

    return render_template("subir_imagen.html", servicios=servicios)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
