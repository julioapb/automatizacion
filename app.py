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
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            c.nombre AS cliente,
            s.referencia,
            s.articulos_por_caja,
            ps.cantidad,
            col.nombre_color AS color,
            col.codigo_html AS codigo_html
        FROM pedidos p
        JOIN cliente c ON p.id_cliente = c.id_cliente
        JOIN pedido_servicio ps ON p.id_pedido = ps.id_pedido
        JOIN servicio s ON ps.id_servicio = s.id_servicio
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
        ref = r["referencia"]
        color = r["color"] or "-"
        color_html = r["codigo_html"] or "#FFFFFF"
        cantidad = r["cantidad"]
        num_pedido = r["numero_pedido"]
        por_caja = r["articulos_por_caja"] or 1
        fecha = date.today().strftime("%Y-%m-%d")

        num_cajas = math.ceil(cantidad / por_caja)
        resto = cantidad % por_caja

        for i in range(num_cajas):
            cantidad_caja = resto if (i == num_cajas - 1 and resto != 0) else por_caja

            # === CABECERA (más abajo para no tocar la línea) ===
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawCentredString(40 * mm, 42 * mm, ref)

            # === LOGO (esquina superior izquierda) ===
            ruta_logo = "static/img/logo.png"
            if os.path.exists(ruta_logo):
                logo = ImageReader(ruta_logo)
                pdf.drawImage(logo, 3 * mm, 37 * mm, width=12 * mm, height=8 * mm, mask="auto")

            # === IMAGEN IZQUIERDA ===
            ruta_imagen = f"static/img/servicios/{ref}.png"
            img_x = 5 * mm
            img_y = 10 * mm
            img_w = 30 * mm
            img_h = 28 * mm

            if os.path.exists(ruta_imagen):
                img = ImageReader(ruta_imagen)
                pdf.drawImage(img, img_x, img_y, width=img_w, height=img_h, preserveAspectRatio=True)
            else:
                pdf.setFont("Helvetica-Oblique", 8)
                pdf.drawCentredString(img_x + 15 * mm, img_y + 14 * mm, "(Sin imagen)")

            # === CUADRO DE INFORMACIÓN DERECHA ===
            cuadro_x = 37 * mm
            cuadro_y = 10 * mm
            cuadro_w = 40 * mm
            cuadro_h = 30 * mm
            pdf.rect(cuadro_x, cuadro_y, cuadro_w, cuadro_h)

            pdf.setFont("Helvetica", 9)
            line_height = 9
            offset_y = cuadro_y + cuadro_h - 10

            pdf.drawString(cuadro_x + 5, offset_y, f"CANTIDAD: {cantidad_caja}")
            offset_y -= line_height + 2
            pdf.drawString(cuadro_x + 5, offset_y, f"ORD: {num_pedido}")
            offset_y -= line_height + 2
            pdf.drawString(cuadro_x + 5, offset_y, f"FECHA: {fecha}")
            offset_y -= line_height + 2
            pdf.drawString(cuadro_x + 5, offset_y, f"COLOR: {color}")

            # === CÍRCULO DEL COLOR (2 cm más abajo y más a la izquierda) ===
            try:
                pdf.setFillColor(HexColor(color_html))
                pdf.circle(cuadro_x + 10, offset_y - 20, 6, fill=1, stroke=1)
                pdf.setFillColorRGB(0, 0, 0)
            except Exception as e:
                print("Error color:", e)

            # === MARCO EXTERIOR ===
            pdf.rect(2 * mm, 2 * mm, 76 * mm, 46 * mm)
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

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM servicio ORDER BY id_servicio DESC")
    lista_servicios = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("servicios.html", servicios=lista_servicios)


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

    if request.method == "POST":
        referencia = request.form.get("referencia")
        descripcion = request.form.get("descripcion")
        precio = request.form.get("precio")
        articulos_por_caja = request.form.get("articulos_por_caja")

        # --- imagen enviada ---
        imagen = request.files.get("imagen")

        filename = None

        if imagen and allowed_file(imagen.filename):
            filename = secure_filename(f"{referencia}.png")  # SIEMPRE guardará como referencia.png
            imagen.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO servicio (referencia, descripcion, precio, articulos_por_caja)
                VALUES (%s, %s, %s, %s)
            """, (referencia, descripcion, precio, articulos_por_caja))
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
                neto=%s,
                fecha_recepcion=%s
            WHERE id_pedido_servicio=%s
        """

        valores = (
            data.get("cantidad"),
            data.get("precio_unitario"),
            data.get("descuento"),
            data.get("neto"),
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

    if request.method == "POST":
        if 'imagen' not in request.files:
            flash("No se seleccionó ningún archivo", "warning")
            return redirect(request.url)
        
        file = request.files['imagen']
        referencia = request.form.get("referencia", "").strip()

        if file.filename == '':
            flash("Archivo no seleccionado", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            extension = filename.rsplit('.', 1)[1].lower()

            # Guardar con el nombre de referencia (ej: 52-0154-001.png)
            if referencia:
                filename = f"{referencia}.{extension}"

            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            flash("Imagen subida correctamente ✅", "success")
            return redirect(url_for("subir_imagen"))

        flash("Formato de archivo no permitido ❌", "danger")
        return redirect(request.url)

    return render_template("subir_imagen.html")



if __name__ == "__main__":
    app.run(debug=True)



