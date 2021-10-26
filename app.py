from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.utils import secure_filename
import os
import pathlib
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "llave_secreta"



conexion = sqlite3.connect('database/ecommerce.db', check_same_thread=False)
cursor = conexion.cursor()
conexion.commit()




def carro():
    idusuario = session["id"]
    cursor.execute("SELECT DISTINCT productos.id FROM productos, carrito WHERE carrito.id_producto = productos.id AND carrito.id_usuario = ? ORDER BY productos.id DESC", (idusuario,))
    filas = cursor.fetchall()
    cantidad = len(filas)
    session["carrito"] = cantidad


@app.before_request
def verificar():
    ruta = request.path
    if not 'usuario' in session and ruta != "/login" and ruta != "/loguear" and ruta != "/registro" and not ruta.startswith("/static"):
        flash("Inicia sesión para continuar")
        return redirect("/login")


@app.route('/')
@app.route('/index')
@app.route('/inicio')
def index():
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos WHERE cantidad > 0 ORDER BY id DESC LIMIT 8")
    filas = cursor.fetchall()
    return render_template('inicio.html', filas = filas)



@app.route("/login")
def login():
    return render_template("login.html")



@app.route('/cerrar_session')
def cerrar_session():
    session.clear()
    return redirect(url_for('login'))


@app.route('/loguear', methods=['POST'])
def loguear():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']

        if not (correo and contrasena):
            flash("Rellene todos los campos")
            return redirect(url_for('login'))
        else:
            correo = correo.strip()
            contrasena = contrasena.strip()
        cursor.execute("SELECT * FROM usuarios WHERE correo=? ", (correo,))
        filas = cursor.fetchone()
        

        if not filas or not check_password_hash(filas[4], contrasena):
            flash("Correo o contrasena incorrectos")
        else:
            session["usuario"] = filas[1]
            session["id"] = filas[0]
            session["rol"] = filas[6]
            return redirect(url_for('index'))
    return render_template('login.html')
        


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        contrasenah = generate_password_hash(contrasena)
        pais = request.form['pais']

        if not (nombre and contrasena):
            flash("Rellene todos los campos")
            return redirect(url_for('registro'))
        else:
            nombre = nombre.strip()
            apellido = apellido.strip()
            correo = correo.strip()
            contrasena = contrasena.strip()
            pais = pais.strip()
        
        cursor.execute("SELECT * FROM usuarios WHERE correo=? ", (correo,))
        filas = cursor.fetchone()

        if not filas:
            cursor.execute("INSERT INTO usuarios(nombre,apellido,correo,contrasena,pais,id_rol) VALUES (?,?,?,?,?,?)", (nombre,apellido,correo,contrasenah,pais,1))
            conexion.commit()
            flash("Cuenta creada exitosamente")
            return redirect(url_for('login'))
    return render_template("registro.html")



@app.route('/comentar', methods=['POST'])
def comentar():
    if request.method == 'POST':
        id = request.form['identificador']
        comentario = request.form['comentario']
        idusuario = session['id']
        fecha = datetime.today().strftime('%Y-%m-%d %H:%M')
        cursor.execute("INSERT INTO comentarios(usuario, id_producto, comentario, fecha) VALUES (?,?,?,?)", (session["usuario"], id, comentario, fecha))
        conexion.commit()
    return redirect(url_for('productodetalle', id = id))


@app.route('/eliminar_comentario/<id>/<ide>', methods=['GET'])
def eliminar_comentario(id,ide):
    cursor.execute("DELETE FROM comentarios WHERE id=?", (id,))
    conexion.commit()
    return redirect(url_for('productodetalle', id = ide))




@app.route('/producto', methods=['GET'])
def producto():
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos ORDER BY id DESC")
    filas = cursor.fetchall()
    return render_template("producto.html", filas = filas)




@app.route('/<id>', methods=['GET'])
def productodetalle(id):
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    session["identificador"] = id
    cursor.execute("SELECT * FROM productos WHERE id=?", (id,))
    productos = cursor.fetchall()
    cursor.execute("SELECT id, usuario, id_producto, comentario, fecha FROM comentarios WHERE id_producto=?", (id,))
    comentarios = cursor.fetchall()
    return render_template("producto-detalle.html", productos = productos, comentarios = comentarios)



@app.route('/favoritos')
def favoritos():
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    idusuario = session['id']
    cursor.execute("SELECT DISTINCT productos.id, productos.nombre, productos.precio, productos.cantidad, productos.imagen FROM productos, favoritos WHERE favoritos.id_producto = productos.id AND favoritos.id_usuario = ? ORDER BY productos.id DESC", (idusuario,))
    filas = cursor.fetchall()
    return render_template("favoritos.html", filas = filas)




@app.route('/carrito')
def carrito():
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    idusuario = session['id']
    cursor.execute("SELECT DISTINCT productos.id, productos.nombre, productos.precio, productos.cantidad, productos.imagen FROM productos, carrito WHERE carrito.id_producto = productos.id AND carrito.id_usuario = ? ORDER BY productos.id DESC", (idusuario,))
    filas = cursor.fetchall()
    ids = [row[0] for row in filas]
    total = sum(row[2] for row in filas)
    cantidad = len(filas)
    return render_template("carrito.html", filas = filas, total = total, cantidad = cantidad, id = ids)




@app.route('/comprar/<id>', methods=['GET', 'POST'])
def comprar(id):
    idusuario = session['id']
    fecha = datetime.today().strftime('%Y-%m-%d %H:%M')
    cursor.execute("INSERT INTO compras(id_usuario, id_producto, cantidad, fecha) VALUES (?,?,?,?)", (idusuario, id, 1, fecha))
    cursor.execute("UPDATE productos SET cantidad = cantidad - 1 WHERE id = ?", (id,))
    cursor.execute("DELETE FROM carrito WHERE id_usuario = ? AND id_producto = ?", (idusuario,id))
    conexion.commit()
    carro()
    return redirect(url_for('carrito'))


@app.route('/comprartodo', methods=['GET', 'POST'])
def comprartodo():
    idusuario = session['id']
    cursor.execute("SELECT DISTINCT productos.id FROM productos, carrito WHERE carrito.id_producto = productos.id AND carrito.id_usuario = ? ", (idusuario,))
    filas = cursor.fetchall()
    fecha = datetime.today().strftime('%Y-%m-%d %H:%M')
    for fila in filas:
        cursor.execute("INSERT INTO compras(id_usuario, id_producto, cantidad, fecha) VALUES (?,?,?,?)", (idusuario, fila[0], 1, fecha))
        cursor.execute("UPDATE productos SET cantidad = cantidad - 1 WHERE id = ?", (fila[0],))
        cursor.execute("DELETE FROM carrito WHERE id_usuario = ? AND id_producto = ?", (idusuario,fila[0]))
    conexion.commit()
    carro()
    return redirect(url_for('carrito'))



@app.route('/agregar_carrito/<id>', methods=['GET'])
def agregar_carrito(id):
    idusuario = session['id']
    cursor.execute("INSERT INTO carrito(id_usuario, id_producto) VALUES (?,?)", (idusuario, id))
    conexion.commit()
    carro()
    return redirect(url_for('producto'))



@app.route('/eliminar_carrito/<id>', methods=['GET'])
def eliminar_carrito(id):
    idusuario = session['id']
    cursor.execute("DELETE FROM carrito WHERE id_usuario=? AND id_producto=?", (idusuario, id))
    conexion.commit()
    carro()
    return redirect(url_for('carrito'))




@app.route('/agregar_favoritos/<id>', methods=['GET'])
def agregar_favoritos(id):
    idusuario = session['id']
    cursor.execute("INSERT INTO favoritos(id_usuario, id_producto) VALUES (?,?)", (idusuario, id))
    conexion.commit()
    return redirect(url_for('producto'))



@app.route('/eliminar_favorito/<id>', methods=['GET'])
def eliminar_favorito(id):
    idusuario = session['id']
    cursor.execute("DELETE FROM favoritos WHERE id_usuario=? AND id_producto=?", (idusuario, id))
    conexion.commit()
    return redirect(url_for('favoritos'))




@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if session['rol'] == 1 :
        return redirect("/inicio")

    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos")
    filas = cursor.fetchall()
    return render_template("admin.html", filas = filas)




@app.route('/admin_usuarios', methods=['GET', 'POST'])
def admin_usuarios():
    if session['rol'] != 3 :
        return redirect("/inicio")
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios")
    filas = cursor.fetchall()
    return render_template("admin-usuarios.html", filas = filas)


@app.route('/actualizar_usuario', methods=['GET', 'POST'])
def actualizar_usuario():
    if request.method == 'POST':
        id = request.form['id']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo = request.form['correo']
        pais = request.form['pais']
        rol = request.form['rol']
        cursor.execute("UPDATE usuarios SET nombre = ?, apellido = ?, correo = ?, pais = ?, id_rol = ? WHERE id = ?", (nombre,apellido,correo,pais,rol,id))
        conexion.commit()
        flash("Usuario Actualizado Exitosamente")
        return redirect(url_for('admin_usuarios'))



@app.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        descripcion = request.form['descripcion']
        cantidad = request.form['cantidad']
        estado = request.form['estado']
        cursor.execute("INSERT INTO productos(nombre,precio,descripcion,cantidad,estado,imagen) VALUES (?,?,?,?,?,?)", (nombre,precio,descripcion,cantidad,estado,0))
        conexion.commit()
        cursor.execute("SELECT id FROM productos ORDER BY id DESC LIMIT 1")
        idproducto = cursor.fetchone()

        if 'imagen' not in request.files:
            return 'there is no file1 in form!'
        file1 = request.files['imagen']
        ide = str(idproducto)
        identificador = ''.join(filter(str.isalnum, ide))
        ruta = 'static/productos/' + identificador
        os.mkdir(ruta)
        UPLOAD_FOLDER = ruta
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        file1.save(path)
        #return path
        
        for filename in os.listdir(ruta):
            rutaimagen = os.path.join(ruta,filename)
        cursor.execute("UPDATE productos SET imagen = ? WHERE id = ?", (rutaimagen,identificador))
        conexion.commit()


        flash("Producto Agregado Exitosamente")
    return redirect(url_for('admin'))




@app.route('/actualizar_producto', methods=['GET', 'POST'])
def actualizar_producto():
    if request.method == 'POST':
        id = request.form['id']
        nombre = request.form['nombre']
        precio = request.form['precio']
        descripcion = request.form['descripcion']
        cantidad = request.form['cantidad']
        estado = request.form['estado']
        imagen = request.form['imagen']
        cursor.execute("UPDATE productos SET nombre = ?, precio = ?, descripcion = ?, cantidad = ?, estado = ?, imagen = ? WHERE id = ?", (nombre,precio,descripcion,cantidad,estado,imagen,id))
        conexion.commit()
        flash("Producto Actualizado Exitosamente")
        return redirect(url_for('admin'))




@app.route('/eliminar_producto/<id>/', methods=['GET', 'POST'])
def eliminar_producto(id):
    int(id)
    cursor.execute("DELETE FROM productos WHERE id=?", (id,))
    conexion.commit()
    flash("Producto Eliminado Exitosamente")
    return redirect(url_for('admin'))




if __name__ == '__main__':
    app.run(debug=True)