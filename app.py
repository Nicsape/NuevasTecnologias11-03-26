from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request
import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps

# -------------------------------
# Inicialización de la aplicación
# -------------------------------
app = Flask(__name__)
app.secret_key = 'clave_secreta_gimnasio'

# Configuración de JWT con cookies
app.config['JWT_SECRET_KEY'] = 'clave_ultra_secreta_jwt_2025'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False          # Cambiar a True en HTTPS
app.config['JWT_COOKIE_HTTPONLY'] = True
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

jwt = JWTManager(app)

# -------------------------------
# Conexiones a bases de datos
# -------------------------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='12345',
            database='monster gym',
            auth_plugin='mysql_native_password'
        )
        return conn
    except Error as e:
        print(f"Error de conexión MySQL: {e}")
        return None

client = MongoClient("mongodb://localhost:27017/")
db_mongo = client["Gym"]
coleccion_notificaciones = db_mongo["notificaciones"]

# -------------------------------
# Función auxiliar para obtener roles del usuario actual
# -------------------------------
def get_current_user_roles():
    """Devuelve lista de roles del usuario actual (requiere JWT validado previamente)"""
    try:
        user_id = get_jwt_identity()
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.Nombre_Rol FROM usuario_rol ur
            JOIN rol r ON ur.FK_ID_Rol = r.ID_Rol
            WHERE ur.FK_ID_Usuario = %s
        """, (user_id,))
        roles = [row['Nombre_Rol'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return roles
    except:
        return []

# -------------------------------
# Decorador para control de roles (RBAC)
# -------------------------------
def role_required(required_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
            except Exception as e:
                print(f"❌ Error de JWT en {request.path}: {e}")
                flash('Debes iniciar sesión para acceder', 'warning')
                return redirect(url_for('login_page'))

            conn = get_db_connection()
            if not conn:
                flash('Error de conexión a la base de datos', 'error')
                return redirect(url_for('home'))
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.Nombre_Rol FROM usuario_rol ur
                JOIN rol r ON ur.FK_ID_Rol = r.ID_Rol
                WHERE ur.FK_ID_Usuario = %s
            """, (current_user_id,))
            roles = [row['Nombre_Rol'] for row in cursor.fetchall()]
            cursor.close()
            conn.close()

            if not roles:
                flash('Usuario sin roles asignados', 'error')
                return redirect(url_for('login_page'))

            if isinstance(required_roles, str):
                roles_requeridos = [required_roles]
            else:
                roles_requeridos = required_roles

            if any(role in roles_requeridos for role in roles):
                return fn(*args, **kwargs)
            else:
                flash('Permisos insuficientes', 'error')
                return redirect(url_for('home'))
        return wrapper
    return decorator

# -------------------------------
# Rutas públicas
# -------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/register_page')
def register_page():
    return render_template('register.html')

# -------------------------------
# Autenticación (API)
# -------------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    telefono = data.get('telefono')
    direccion = data.get('direccion')
    edad = data.get('edad')
    seguro = data.get('seguro')

    if not all([nombre, apellido, email, username, password]):
        return jsonify({"msg": "Faltan datos obligatorios"}), 400

    hashed_pw = generate_password_hash(password)

    conn = get_db_connection()
    if not conn:
        return jsonify({"msg": "Error de conexión"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_Usuario FROM Usuario WHERE Email = %s OR Username = %s", (email, username))
        if cursor.fetchone():
            return jsonify({"msg": "Email o nombre de usuario ya existe"}), 400

        cursor.execute("SELECT MAX(ID_Usuario) FROM Usuario")
        max_id = cursor.fetchone()[0]
        next_id = (max_id or 0) + 1

        fecha_registro = datetime.now().date()
        cursor.execute("""
            INSERT INTO Usuario (ID_Usuario, Nombre, Apellido, Email, Username, Password_Hash,
                                 Telefono, Direccion, Edad, Seguro, Fecha_Registro, Activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
        """, (next_id, nombre, apellido, email, username, hashed_pw,
              telefono, direccion, edad, seguro, fecha_registro))

        # Asignar rol CLIENTE por defecto
        cursor.execute("SELECT ID_Rol FROM rol WHERE Nombre_Rol = 'CLIENTE'")
        rol_cliente = cursor.fetchone()
        if rol_cliente:
            cursor.execute("INSERT INTO usuario_rol (FK_ID_Usuario, FK_ID_Rol) VALUES (%s, %s)",
                           (next_id, rol_cliente[0]))
        conn.commit()
        return jsonify({"msg": "Usuario registrado exitosamente"}), 201
    except Error as e:
        conn.rollback()
        return jsonify({"msg": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    if not conn:
        return jsonify({"msg": "Error de conexión"}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT ID_Usuario, Password_Hash FROM Usuario WHERE Username = %s AND Activo = 1", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not check_password_hash(user['Password_Hash'], password):
        return jsonify({"msg": "Credenciales inválidas"}), 401

    access_token = create_access_token(identity=str(user['ID_Usuario']))
    response = jsonify({"msg": "Login exitoso", "user_id": user['ID_Usuario']})
    set_access_cookies(response, access_token)
    return response, 200

@app.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"msg": "Sesión cerrada"})
    unset_jwt_cookies(response)
    return response

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    if not conn:
        return jsonify({"msg": "Error de conexión"}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT ID_Usuario, Nombre, Apellido, Email, Username, Telefono, Direccion, Edad, Seguro, Fecha_Registro
        FROM Usuario WHERE ID_Usuario = %s
    """, (current_user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    return jsonify(user), 200

# -------------------------------
# Inventario (solo ADMIN)
# -------------------------------
@app.route('/inventario')
@role_required('ADMIN')
def inventario():
    conn = get_db_connection()
    inventario_items = []
    error = None
    if not conn:
        error = "No se pudo conectar a la base de datos."
    else:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT i.CodigoInv, p.Nombre AS Producto, p.Categoria, i.Stock, p.Precio
                FROM inventario i
                JOIN producto p ON i.FK_ID_Producto = p.ID_Producto
            """)
            inventario_items = cursor.fetchall()
            cursor.close()
            conn.close()
        except Error as e:
            error = f"Error: {str(e)}"
    return render_template('inventario.html', inventario_items=inventario_items, error=error)

@app.route('/registrar_inventario', methods=['GET'])
@role_required('ADMIN')
def registrar_inventario():
    return render_template('registrar_inventario.html')

@app.route('/registrar_inventario', methods=['POST'])
@role_required('ADMIN')
def registrar_inventario_post():
    producto = request.form.get('producto')
    categoria = request.form.get('categoria')
    stock = request.form.get('stock')
    precio = request.form.get('precio')

    if not all([producto, categoria, stock, precio]):
        flash('Todos los campos son obligatorios.', 'error')
        return redirect(url_for('registrar_inventario'))

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(ID_Producto) FROM producto")
            max_id = cursor.fetchone()[0]
            new_id = (max_id or 0) + 1
            cursor.execute(
                "INSERT INTO producto (ID_Producto, Nombre, Categoria, Precio) VALUES (%s, %s, %s, %s)",
                (new_id, producto, categoria, float(precio))
            )
            stock_int = int(stock)
            if stock_int < 0 or stock_int > 100:
                flash('El stock debe estar entre 0 y 100', 'error')
                return redirect(url_for('inventario'))
            cursor.execute(
                "INSERT INTO inventario (FK_ID_Producto, Stock) VALUES (%s, %s)",
                (new_id, stock_int)
            )
            conn.commit()
            flash('Producto agregado exitosamente', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('inventario'))

@app.route('/editar_inventario/<int:codigo_inv>', methods=['GET'])
@role_required('ADMIN')
def editar_inventario(codigo_inv):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT i.CodigoInv, p.ID_Producto, p.Nombre AS Producto, p.Categoria, i.Stock, p.Precio
                FROM inventario i
                JOIN producto p ON i.FK_ID_Producto = p.ID_Producto
                WHERE i.CodigoInv = %s
            """, (codigo_inv,))
            item = cursor.fetchone()
            cursor.close()
            conn.close()
            if item:
                return render_template('editar_inventario.html', item=item)
            else:
                flash('Producto no encontrado', 'error')
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('inventario'))

@app.route('/editar_inventario/<int:codigo_inv>', methods=['POST'])
@role_required('ADMIN')
def editar_inventario_post(codigo_inv):
    producto = request.form.get('producto')
    categoria = request.form.get('categoria')
    stock = request.form.get('stock')
    precio = request.form.get('precio')

    if not all([producto, categoria, stock, precio]):
        flash('Todos los campos son obligatorios.', 'error')
        return redirect(url_for('editar_inventario', codigo_inv=codigo_inv))

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT FK_ID_Producto FROM inventario WHERE CodigoInv = %s", (codigo_inv,))
            result = cursor.fetchone()
            if not result:
                flash('Producto no encontrado', 'error')
                return redirect(url_for('inventario'))
            fk_producto = result[0]
            cursor.execute(
                "UPDATE producto SET Nombre = %s, Categoria = %s, Precio = %s WHERE ID_Producto = %s",
                (producto, categoria, float(precio), fk_producto)
            )
            stock_int = int(stock)
            if stock_int < 0 or stock_int > 100:
                flash('El stock debe estar entre 0 y 100', 'error')
                return redirect(url_for('inventario'))
            cursor.execute(
                "UPDATE inventario SET Stock = %s WHERE CodigoInv = %s",
                (stock_int, codigo_inv)
            )
            conn.commit()
            flash('Producto actualizado', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('inventario'))

@app.route('/eliminar_inventario/<int:codigo_inv>', methods=['POST'])
@role_required('ADMIN')
def eliminar_inventario(codigo_inv):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT FK_ID_Producto FROM inventario WHERE CodigoInv = %s", (codigo_inv,))
            result = cursor.fetchone()
            if result:
                fk = result[0]
                cursor.execute("DELETE FROM producto WHERE ID_Producto = %s", (fk,))
            else:
                cursor.execute("DELETE FROM inventario WHERE CodigoInv = %s", (codigo_inv,))
            conn.commit()
            flash('Producto eliminado', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('inventario'))

# -------------------------------
# Máquinas (ADMIN y RECEPCIONISTA)
# -------------------------------
@app.route('/maquinas')
@role_required(['ADMIN', 'RECEPCIONISTA'])
def maquinas():
    conn = get_db_connection()
    maquinas_list = []
    error = None
    if not conn:
        error = "No se pudo conectar."
    else:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT CodigoMaq, Nombre, Categoria FROM maquinas")
            maquinas_list = cursor.fetchall()
            cursor.close()
            conn.close()
        except Error as e:
            error = f"Error: {str(e)}"
    return render_template('maquinas.html', maquinas_list=maquinas_list, error=error)

@app.route('/registrar_maquina', methods=['GET'])
@role_required(['ADMIN', 'RECEPCIONISTA'])
def registrar_maquina():
    return render_template('registrar_maquina.html')

@app.route('/registrar_maquina', methods=['POST'])
@role_required(['ADMIN', 'RECEPCIONISTA'])
def registrar_maquina_post():
    nombre = request.form.get('nombre')
    categoria = request.form.get('categoria')
    if not all([nombre, categoria]):
        flash('Todos los campos son obligatorios.', 'error')
        return redirect(url_for('registrar_maquina'))
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(CodigoMaq) FROM maquinas")
            max_code = cursor.fetchone()[0]
            next_code = (max_code or 0) + 1
            cursor.execute(
                "INSERT INTO maquinas (CodigoMaq, Nombre, Categoria) VALUES (%s, %s, %s)",
                (next_code, nombre, categoria)
            )
            conn.commit()
            flash('Máquina agregada', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('maquinas'))

@app.route('/editar_maquina/<int:codigo_maq>', methods=['GET'])
@role_required(['ADMIN', 'RECEPCIONISTA'])
def editar_maquina(codigo_maq):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM maquinas WHERE CodigoMaq = %s", (codigo_maq,))
            maquina = cursor.fetchone()
            cursor.close()
            conn.close()
            if maquina:
                return render_template('editar_maquina.html', maquina=maquina)
            else:
                flash('Máquina no encontrada', 'error')
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('maquinas'))

@app.route('/editar_maquina/<int:codigo_maq>', methods=['POST'])
@role_required(['ADMIN', 'RECEPCIONISTA'])
def editar_maquina_post(codigo_maq):
    nombre = request.form.get('nombre')
    categoria = request.form.get('categoria')
    if not all([nombre, categoria]):
        flash('Todos los campos son obligatorios.', 'error')
        return redirect(url_for('editar_maquina', codigo_maq=codigo_maq))
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE maquinas SET Nombre = %s, Categoria = %s WHERE CodigoMaq = %s",
                (nombre, categoria, codigo_maq)
            )
            conn.commit()
            flash('Máquina actualizada', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('maquinas'))

@app.route('/eliminar_maquina/<int:codigo_maq>', methods=['POST'])
@role_required(['ADMIN', 'RECEPCIONISTA'])
def eliminar_maquina(codigo_maq):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM maquinas WHERE CodigoMaq = %s", (codigo_maq,))
            conn.commit()
            flash('Máquina eliminada', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('maquinas'))

# -------------------------------
# Usuarios (ADMIN y RECEPCIONISTA) - con control de roles para recepcionistas
# -------------------------------
@app.route('/usuarios')
@role_required(['ADMIN', 'RECEPCIONISTA'])
def usuarios():
    conn = get_db_connection()
    usuarios_list = []
    error = None
    if not conn:
        error = "Error de conexión"
    else:
        try:
            cursor = conn.cursor(dictionary=True)
            current_roles = get_current_user_roles()
            if 'ADMIN' in current_roles:
                # Admin ve todos los usuarios
                cursor.execute("""
                    SELECT u.ID_Usuario, u.Nombre, u.Apellido, u.Telefono, u.Direccion, u.Edad, u.Seguro, u.Fecha_Registro,
                           tm.Plan as Membresia_Plan, tm.Costo as Membresia_Costo, tm.Duracion_Meses as Membresia_Duracion,
                           mu.Fecha_Inicio, mu.Fecha_Fin
                    FROM Usuario u
                    LEFT JOIN membresia_usuario mu ON u.ID_Usuario = mu.FK_ID_Usuario
                    LEFT JOIN tipo_membresia tm ON mu.FK_ID_Tipo = tm.ID_Tipo
                """)
            else:
                # Recepcionista solo ve usuarios con rol CLIENTE
                cursor.execute("""
                    SELECT u.ID_Usuario, u.Nombre, u.Apellido, u.Telefono, u.Direccion, u.Edad, u.Seguro, u.Fecha_Registro,
                           tm.Plan as Membresia_Plan, tm.Costo as Membresia_Costo, tm.Duracion_Meses as Membresia_Duracion,
                           mu.Fecha_Inicio, mu.Fecha_Fin
                    FROM Usuario u
                    LEFT JOIN membresia_usuario mu ON u.ID_Usuario = mu.FK_ID_Usuario
                    LEFT JOIN tipo_membresia tm ON mu.FK_ID_Tipo = tm.ID_Tipo
                    WHERE EXISTS (
                        SELECT 1 FROM usuario_rol ur
                        JOIN rol r ON ur.FK_ID_Rol = r.ID_Rol
                        WHERE ur.FK_ID_Usuario = u.ID_Usuario AND r.Nombre_Rol = 'CLIENTE'
                    )
                """)
            usuarios_list = cursor.fetchall()
            cursor.close()
            conn.close()
        except Error as e:
            error = f"Error: {str(e)}"
    return render_template('usuarios.html', usuarios_list=usuarios_list, error=error)

@app.route('/registrar_usuario', methods=['GET'])
@role_required(['ADMIN', 'RECEPCIONISTA'])
def registrar_usuario():
    es_admin = 'ADMIN' in get_current_user_roles()
    return render_template('registrar_usuario.html', es_admin=es_admin)

@app.route('/registrar_usuario', methods=['POST'])
@role_required(['ADMIN', 'RECEPCIONISTA'])
def registrar_usuario_post():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')
    edad = request.form.get('edad')
    seguro = request.form.get('seguro')
    fecha_registro = request.form.get('fecha_registro')
    plan_membresia = request.form.get('plan_membresia')
    duracion_membresia = request.form.get('duracion_membresia')
    rol_nombre = request.form.get('rol', 'CLIENTE')   # puede venir del formulario

    if not all([nombre, apellido, email, username, password, telefono, direccion, edad, seguro, fecha_registro]):
        flash('Todos los campos obligatorios deben ser completados.', 'error')
        return redirect(url_for('registrar_usuario'))

    # Forzar rol CLIENTE si el usuario logueado no es admin
    current_roles = get_current_user_roles()
    if 'ADMIN' not in current_roles:
        rol_nombre = 'CLIENTE'

    hashed_pw = generate_password_hash(password)
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(ID_Usuario) FROM Usuario")
            max_id = cursor.fetchone()[0]
            next_id = (max_id or 0) + 1
            cursor.execute("""
                INSERT INTO Usuario (ID_Usuario, Nombre, Apellido, Email, Username, Password_Hash,
                                     Telefono, Direccion, Edad, Seguro, Fecha_Registro, Activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            """, (next_id, nombre, apellido, email, username, hashed_pw,
                  telefono, direccion, int(edad), seguro, fecha_registro))

            # Asignar rol (forzado a CLIENTE para recepcionistas)
            cursor.execute("SELECT ID_Rol FROM rol WHERE Nombre_Rol = %s", (rol_nombre,))
            rol = cursor.fetchone()
            if rol:
                cursor.execute("INSERT INTO usuario_rol (FK_ID_Usuario, FK_ID_Rol) VALUES (%s, %s)", (next_id, rol[0]))
            else:
                # fallback
                cursor.execute("SELECT ID_Rol FROM rol WHERE Nombre_Rol = 'CLIENTE'")
                default_rol = cursor.fetchone()
                if default_rol:
                    cursor.execute("INSERT INTO usuario_rol (FK_ID_Usuario, FK_ID_Rol) VALUES (%s, %s)", (next_id, default_rol[0]))

            # Membresía (opcional)
            if plan_membresia and duracion_membresia:
                cursor.execute("SELECT ID_Tipo FROM tipo_membresia WHERE Plan = %s AND Duracion_Meses = %s",
                               (plan_membresia, int(duracion_membresia)))
                tipo = cursor.fetchone()
                if tipo:
                    fecha_ini = datetime.now().date()
                    fecha_fin = fecha_ini + timedelta(days=int(duracion_membresia)*30)
                    cursor.execute("""
                        INSERT INTO membresia_usuario (FK_ID_Usuario, FK_ID_Tipo, Fecha_Inicio, Fecha_Fin)
                        VALUES (%s, %s, %s, %s)
                    """, (next_id, tipo[0], fecha_ini, fecha_fin))

            conn.commit()
            flash('Usuario registrado exitosamente!', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error al guardar usuario: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('usuarios'))

@app.route('/editar_usuario/<int:id_usuario>', methods=['GET'])
@role_required(['ADMIN', 'RECEPCIONISTA'])
def editar_usuario(id_usuario):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Usuario WHERE ID_Usuario = %s", (id_usuario,))
            usuario = cursor.fetchone()
            cursor.execute("SELECT * FROM membresia_usuario WHERE FK_ID_Usuario = %s", (id_usuario,))
            membresia = cursor.fetchone()
            cursor.close()
            conn.close()
            if usuario:
                es_admin = 'ADMIN' in get_current_user_roles()
                return render_template('editar_usuario.html', usuario=usuario, membresia=membresia, es_admin=es_admin)
            else:
                flash('Usuario no encontrado', 'error')
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('usuarios'))

@app.route('/editar_usuario/<int:id_usuario>', methods=['POST'])
@role_required(['ADMIN', 'RECEPCIONISTA'])
def editar_usuario_post(id_usuario):
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')
    edad = request.form.get('edad')
    seguro = request.form.get('seguro')
    fecha_registro = request.form.get('fecha_registro')
    plan_membresia = request.form.get('plan_membresia')
    duracion_membresia = request.form.get('duracion_membresia')

    if not all([nombre, apellido, telefono, direccion, edad, seguro, fecha_registro]):
        flash('Todos los campos obligatorios', 'error')
        return redirect(url_for('editar_usuario', id_usuario=id_usuario))

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Usuario SET Nombre=%s, Apellido=%s, Telefono=%s, Direccion=%s, Edad=%s, Seguro=%s, Fecha_Registro=%s
                WHERE ID_Usuario=%s
            """, (nombre, apellido, telefono, direccion, int(edad), seguro, fecha_registro, id_usuario))

            # Si el usuario actual es admin, puede modificar membresía (el rol no se edita aquí)
            if plan_membresia and duracion_membresia:
                cursor.execute("SELECT ID_Tipo FROM tipo_membresia WHERE Plan=%s AND Duracion_Meses=%s",
                               (plan_membresia, int(duracion_membresia)))
                tipo = cursor.fetchone()
                if tipo:
                    cursor.execute("SELECT ID_Membresia FROM membresia_usuario WHERE FK_ID_Usuario=%s", (id_usuario,))
                    if cursor.fetchone():
                        cursor.execute("UPDATE membresia_usuario SET FK_ID_Tipo=%s WHERE FK_ID_Usuario=%s", (tipo[0], id_usuario))
                    else:
                        fecha_ini = datetime.now().date()
                        fecha_fin = fecha_ini + timedelta(days=int(duracion_membresia)*30)
                        cursor.execute("""
                            INSERT INTO membresia_usuario (FK_ID_Usuario, FK_ID_Tipo, Fecha_Inicio, Fecha_Fin)
                            VALUES (%s, %s, %s, %s)
                        """, (id_usuario, tipo[0], fecha_ini, fecha_fin))

            conn.commit()
            flash('Usuario actualizado', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('usuarios'))

@app.route('/eliminar_usuario/<int:id_usuario>', methods=['POST'])
@role_required('ADMIN')   # solo admin puede eliminar
def eliminar_usuario(id_usuario):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM membresia_usuario WHERE FK_ID_Usuario=%s", (id_usuario,))
            cursor.execute("DELETE FROM usuario_rol WHERE FK_ID_Usuario=%s", (id_usuario,))
            cursor.execute("DELETE FROM Usuario WHERE ID_Usuario=%s", (id_usuario,))
            conn.commit()
            flash('Usuario eliminado', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('usuarios'))

# -------------------------------
# Personal (solo ADMIN)
# -------------------------------
@app.route('/personal')
@role_required('ADMIN')
def personal():
    conn = get_db_connection()
    personal_list = []
    error = None
    if not conn:
        error = "Error de conexión"
    else:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.ID_Usuario, u.Nombre, u.Apellido, r.Nombre_Rol AS Rol, u.Salario, u.Fecha_Contratacion
                FROM Usuario u
                JOIN usuario_rol ur ON u.ID_Usuario = ur.FK_ID_Usuario
                JOIN rol r ON ur.FK_ID_Rol = r.ID_Rol
                WHERE r.Nombre_Rol IN ('ENTRENADOR', 'RECEPCIONISTA', 'ADMIN')
            """)
            personal_list = cursor.fetchall()
            cursor.close()
            conn.close()
        except Error as e:
            error = f"Error: {str(e)}"
    return render_template('personal.html', personal_list=personal_list, error=error)

@app.route('/registrar_personal', methods=['GET'])
@role_required('ADMIN')
def registrar_personal():
    return render_template('registrar_personal.html')

@app.route('/registrar_personal', methods=['POST'])
@role_required('ADMIN')
def registrar_personal_post():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    rol = request.form.get('rol')
    salario = request.form.get('salario')
    fecha_contratacion = request.form.get('fecha_contratacion')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')
    edad = request.form.get('edad')
    seguro = request.form.get('seguro')

    if not all([nombre, apellido, email, username, password, rol, salario, fecha_contratacion]):
        flash('Todos los campos obligatorios', 'error')
        return redirect(url_for('registrar_personal'))

    hashed_pw = generate_password_hash(password)
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(ID_Usuario) FROM Usuario")
            max_id = cursor.fetchone()[0]
            next_id = (max_id or 0) + 1
            cursor.execute("""
                INSERT INTO Usuario (ID_Usuario, Nombre, Apellido, Email, Username, Password_Hash,
                                     Telefono, Direccion, Edad, Seguro, Salario, Fecha_Contratacion, Fecha_Registro, Activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURDATE(), 1)
            """, (next_id, nombre, apellido, email, username, hashed_pw,
                  telefono, direccion, int(edad) if edad else None, seguro, float(salario), fecha_contratacion))
            cursor.execute("SELECT ID_Rol FROM rol WHERE Nombre_Rol = %s", (rol,))
            rol_id = cursor.fetchone()
            if rol_id:
                cursor.execute("INSERT INTO usuario_rol (FK_ID_Usuario, FK_ID_Rol) VALUES (%s, %s)", (next_id, rol_id[0]))
            else:
                flash('Rol no válido', 'error')
                return redirect(url_for('registrar_personal'))
            conn.commit()
            flash('Personal registrado', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('personal'))

@app.route('/editar_personal/<int:id_personal>', methods=['GET'])
@role_required('ADMIN')
def editar_personal(id_personal):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Usuario WHERE ID_Usuario = %s", (id_personal,))
            personal = cursor.fetchone()
            cursor.close()
            conn.close()
            if personal:
                return render_template('editar_personal.html', personal=personal)
            else:
                flash('Personal no encontrado', 'error')
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('personal'))

@app.route('/editar_personal/<int:id_personal>', methods=['POST'])
@role_required('ADMIN')
def editar_personal_post(id_personal):
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')
    edad = request.form.get('edad')
    seguro = request.form.get('seguro')
    salario = request.form.get('salario')
    fecha_contratacion = request.form.get('fecha_contratacion')

    if not all([nombre, apellido, telefono, direccion, salario, fecha_contratacion]):
        flash('Todos los campos obligatorios', 'error')
        return redirect(url_for('editar_personal', id_personal=id_personal))

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Usuario SET Nombre=%s, Apellido=%s, Telefono=%s, Direccion=%s, Edad=%s, Seguro=%s,
                                 Salario=%s, Fecha_Contratacion=%s
                WHERE ID_Usuario=%s
            """, (nombre, apellido, telefono, direccion, int(edad) if edad else None, seguro,
                  float(salario), fecha_contratacion, id_personal))
            conn.commit()
            flash('Personal actualizado', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('personal'))

@app.route('/eliminar_personal/<int:id_personal>', methods=['POST'])
@role_required('ADMIN')
def eliminar_personal(id_personal):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuario_rol WHERE FK_ID_Usuario = %s", (id_personal,))
            cursor.execute("DELETE FROM Usuario WHERE ID_Usuario = %s", (id_personal,))
            conn.commit()
            flash('Personal eliminado', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('personal'))

# -------------------------------
# Distribuidores (solo ADMIN)
# -------------------------------
@app.route('/distribuidores')
@role_required('ADMIN')
def distribuidores():
    conn = get_db_connection()
    distribuidores_list = []
    error = None
    if not conn:
        error = "Error de conexión"
    else:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.ID_Usuario, u.Nombre, u.Apellido, u.Telefono, u.Categoria_Distribuidor AS Categoria
                FROM Usuario u
                JOIN usuario_rol ur ON u.ID_Usuario = ur.FK_ID_Usuario
                JOIN rol r ON ur.FK_ID_Rol = r.ID_Rol
                WHERE r.Nombre_Rol = 'DISTRIBUIDOR'
            """)
            distribuidores_list = cursor.fetchall()
            cursor.close()
            conn.close()
        except Error as e:
            error = f"Error: {str(e)}"
    return render_template('distribuidores.html', distribuidores_list=distribuidores_list, error=error)

@app.route('/registrar_distribuidor', methods=['GET'])
@role_required('ADMIN')
def registrar_distribuidor():
    return render_template('registrar_distribuidor.html')

@app.route('/registrar_distribuidor', methods=['POST'])
@role_required('ADMIN')
def registrar_distribuidor_post():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    telefono = request.form.get('telefono')
    categoria = request.form.get('categoria')
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    if not all([nombre, apellido, telefono, categoria, email, username, password]):
        flash('Todos los campos obligatorios', 'error')
        return redirect(url_for('registrar_distribuidor'))

    hashed_pw = generate_password_hash(password)
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(ID_Usuario) FROM Usuario")
            max_id = cursor.fetchone()[0]
            next_id = (max_id or 0) + 1
            cursor.execute("""
                INSERT INTO Usuario (ID_Usuario, Nombre, Apellido, Email, Username, Password_Hash,
                                     Telefono, Categoria_Distribuidor, Fecha_Registro, Activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE(), 1)
            """, (next_id, nombre, apellido, email, username, hashed_pw, telefono, categoria))
            cursor.execute("SELECT ID_Rol FROM rol WHERE Nombre_Rol = 'DISTRIBUIDOR'")
            rol_id = cursor.fetchone()
            if rol_id:
                cursor.execute("INSERT INTO usuario_rol (FK_ID_Usuario, FK_ID_Rol) VALUES (%s, %s)", (next_id, rol_id[0]))
            conn.commit()
            flash('Distribuidor registrado', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('distribuidores'))

@app.route('/editar_distribuidor/<int:id_distribuidor>', methods=['GET'])
@role_required('ADMIN')
def editar_distribuidor(id_distribuidor):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Usuario WHERE ID_Usuario = %s", (id_distribuidor,))
            distribuidor = cursor.fetchone()
            cursor.close()
            conn.close()
            if distribuidor:
                return render_template('editar_distribuidor.html', distribuidor=distribuidor)
            else:
                flash('Distribuidor no encontrado', 'error')
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('distribuidores'))

@app.route('/editar_distribuidor/<int:id_distribuidor>', methods=['POST'])
@role_required('ADMIN')
def editar_distribuidor_post(id_distribuidor):
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    telefono = request.form.get('telefono')
    categoria = request.form.get('categoria')

    if not all([nombre, apellido, telefono, categoria]):
        flash('Todos los campos obligatorios', 'error')
        return redirect(url_for('editar_distribuidor', id_distribuidor=id_distribuidor))

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Usuario SET Nombre=%s, Apellido=%s, Telefono=%s, Categoria_Distribuidor=%s
                WHERE ID_Usuario=%s
            """, (nombre, apellido, telefono, categoria, id_distribuidor))
            conn.commit()
            flash('Distribuidor actualizado', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('distribuidores'))

@app.route('/eliminar_distribuidor/<int:id_distribuidor>', methods=['POST'])
@role_required('ADMIN')
def eliminar_distribuidor(id_distribuidor):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuario_rol WHERE FK_ID_Usuario = %s", (id_distribuidor,))
            cursor.execute("DELETE FROM Usuario WHERE ID_Usuario = %s", (id_distribuidor,))
            conn.commit()
            flash('Distribuidor eliminado', 'success')
            cursor.close()
            conn.close()
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
    else:
        flash('Error de conexión', 'error')
    return redirect(url_for('distribuidores'))

# -------------------------------
# Notificaciones (MongoDB)
# -------------------------------
@app.route('/notificaciones', methods=['POST'])
@jwt_required()
def crear_notificacion():
    data = request.json
    current_user = get_jwt_identity()
    if data.get('ID_Usuario') != current_user:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.Nombre_Rol FROM usuario_rol ur
            JOIN rol r ON ur.FK_ID_Rol = r.ID_Rol
            WHERE ur.FK_ID_Usuario = %s
        """, (current_user,))
        roles = [row['Nombre_Rol'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if 'ADMIN' not in roles:
            return jsonify({"msg": "No autorizado"}), 403
    resultado = coleccion_notificaciones.insert_one(data)
    return jsonify({"mensaje": "Notificación creada", "id": str(resultado.inserted_id)})

@app.route('/notificaciones', methods=['GET'])
@jwt_required()
def obtener_notificaciones():
    current_user = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.Nombre_Rol FROM usuario_rol ur
        JOIN rol r ON ur.FK_ID_Rol = r.ID_Rol
        WHERE ur.FK_ID_Usuario = %s
    """, (current_user,))
    roles = [row['Nombre_Rol'] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    if 'ADMIN' in roles:
        datos = list(coleccion_notificaciones.find())
    else:
        datos = list(coleccion_notificaciones.find({"ID_Usuario": int(current_user)}))

    for doc in datos:
        doc["_id"] = str(doc["_id"])
    return jsonify(datos)

@app.route('/notificaciones/usuario/<int:id_usuario>', methods=['GET'])
@jwt_required()
def obtener_notificaciones_usuario(id_usuario):
    current_user = get_jwt_identity()
    if current_user != id_usuario:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.Nombre_Rol FROM usuario_rol ur
            JOIN rol r ON ur.FK_ID_Rol = r.ID_Rol
            WHERE ur.FK_ID_Usuario = %s
        """, (current_user,))
        roles = [row['Nombre_Rol'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if 'ADMIN' not in roles:
            return jsonify({"msg": "No autorizado"}), 403
    datos = []
    for doc in coleccion_notificaciones.find({"ID_Usuario": id_usuario}):
        doc["_id"] = str(doc["_id"])
        datos.append(doc)
    return jsonify(datos)

@app.route('/notificaciones/<id>', methods=['PUT'])
@jwt_required()
def actualizar_notificacion(id):
    notif = coleccion_notificaciones.find_one({"_id": ObjectId(id)})
    if not notif:
        return jsonify({"msg": "No encontrada"}), 404
    current_user = get_jwt_identity()
    if notif.get("ID_Usuario") != current_user:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.Nombre_Rol FROM usuario_rol ur
            JOIN rol r ON ur.FK_ID_Rol = r.ID_Rol
            WHERE ur.FK_ID_Usuario = %s
        """, (current_user,))
        roles = [row['Nombre_Rol'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if 'ADMIN' not in roles:
            return jsonify({"msg": "No autorizado"}), 403
    data = request.json
    coleccion_notificaciones.update_one({"_id": ObjectId(id)}, {"$set": data})
    return jsonify({"mensaje": "Notificación actualizada"})

@app.route('/notificaciones/<id>', methods=['DELETE'])
@jwt_required()
def eliminar_notificacion(id):
    notif = coleccion_notificaciones.find_one({"_id": ObjectId(id)})
    if not notif:
        return jsonify({"msg": "No encontrada"}), 404
    current_user = get_jwt_identity()
    if notif.get("ID_Usuario") != current_user:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.Nombre_Rol FROM usuario_rol ur
            JOIN rol r ON ur.FK_ID_Rol = r.ID_Rol
            WHERE ur.FK_ID_Usuario = %s
        """, (current_user,))
        roles = [row['Nombre_Rol'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if 'ADMIN' not in roles:
            return jsonify({"msg": "No autorizado"}), 403
    coleccion_notificaciones.delete_one({"_id": ObjectId(id)})
    return jsonify({"mensaje": "Notificación eliminada"})

@app.route('/usuario/<int:id_usuario>/perfil-completo', methods=['GET'])
@jwt_required()
def perfil_completo(id_usuario):
    current_user = get_jwt_identity()
    if current_user != id_usuario:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.Nombre_Rol FROM usuario_rol ur
            JOIN rol r ON ur.FK_ID_Rol = r.ID_Rol
            WHERE ur.FK_ID_Usuario = %s
        """, (current_user,))
        roles = [row['Nombre_Rol'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        if 'ADMIN' not in roles:
            return jsonify({"msg": "No autorizado"}), 403

    conn = get_db_connection()
    usuario = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Usuario WHERE ID_Usuario = %s", (id_usuario,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

    notificaciones = []
    for doc in coleccion_notificaciones.find({"ID_Usuario": id_usuario}):
        doc["_id"] = str(doc["_id"])
        notificaciones.append(doc)

    return jsonify({"usuario": usuario, "notificaciones": notificaciones})

# -------------------------------
# Inicialización de la base de datos y creación de admin por defecto
# -------------------------------
def init_database():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Verificar existencia de roles
            cursor.execute("SELECT COUNT(*) FROM rol")
            if cursor.fetchone()[0] == 0:
                roles = ['ADMIN', 'CLIENTE', 'ENTRENADOR', 'RECEPCIONISTA', 'DISTRIBUIDOR']
                for r in roles:
                    cursor.execute("INSERT INTO rol (Nombre_Rol) VALUES (%s)", (r,))
            # Verificar si existe al menos un ADMIN
            cursor.execute("""
                SELECT COUNT(*) FROM usuario_rol ur
                JOIN rol r ON ur.FK_ID_Rol = r.ID_Rol
                WHERE r.Nombre_Rol = 'ADMIN'
            """)
            admin_count = cursor.fetchone()[0]
            if admin_count == 0:
                hashed_pw = generate_password_hash('admin123')
                cursor.execute("SELECT MAX(ID_Usuario) FROM Usuario")
                max_id = cursor.fetchone()[0]
                new_id = (max_id or 0) + 1
                cursor.execute("""
                    INSERT INTO Usuario (ID_Usuario, Nombre, Apellido, Email, Username, Password_Hash,
                                         Telefono, Direccion, Edad, Seguro, Fecha_Registro, Activo)
                    VALUES (%s, 'Admin', 'Sistema', 'admin@monster.com', 'admin', %s,
                            '300000000', 'Oficina', 30, 'Ninguno', CURDATE(), 1)
                """, (new_id, hashed_pw))
                cursor.execute("SELECT ID_Rol FROM rol WHERE Nombre_Rol = 'ADMIN'")
                admin_role = cursor.fetchone()
                if admin_role:
                    cursor.execute("INSERT INTO usuario_rol (FK_ID_Usuario, FK_ID_Rol) VALUES (%s, %s)",
                                   (new_id, admin_role[0]))
                conn.commit()
                print("✅ Usuario administrador 'admin' creado con contraseña 'admin123'")
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Error en init_database: {e}")
    else:
        print("No se pudo conectar para inicializar la BD")

# -------------------------------
# Punto de entrada
# -------------------------------
if __name__ == '__main__':
    init_database()
    print("Servidor iniciado. Accede a: http://localhost:5000")
    app.run(debug=True)