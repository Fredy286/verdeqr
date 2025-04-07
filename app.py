from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, g
from flask_mysqldb import MySQL
import pymysql
import os
import qrcode
import io
import base64
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave secreta segura

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'VerdeQR_Optimizada'
app.config['MYSQL_CURSORCLASS'] = pymysql.cursors.DictCursor

# Función para obtener la conexión a la base de datos
def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            db=app.config['MYSQL_DB'],
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

# Verificar conexión a la base de datos
try:
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        print("Conexión a la base de datos establecida correctamente")
except Exception as e:
    print(f"Error al conectar con la base de datos: {str(e)}")
finally:
    if 'connection' in locals():
        connection.close()

# Ruta para la gestión de usuarios registrados
@app.route('/gestion_usuarios', methods=['GET', 'POST'])
def gestion_usuarios():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))
    
    if request.method == 'POST':
        try:
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            correo = request.form['correo']
            telefono = request.form['telefono']
            contrasena = request.form['contrasena']
            rol = request.form['rol']
            
            # Verificar si el correo ya existe
            cursor = get_db().cursor()
            cursor.execute("SELECT IDUsuario FROM Usuario WHERE CorreoElectronico = %s", (correo,))
            if cursor.fetchone():
                flash('El correo electrónico ya está registrado', 'error')
                return redirect(url_for('gestion_usuarios'))
            
            # Insertar nuevo usuario
            cursor.execute("""
                INSERT INTO Usuario (Nombres, Apellidos, CorreoElectronico, Telefono, Contrasena, Estado)
                VALUES (%s, %s, %s, %s, %s, 1)
            """, (nombres, apellidos, correo, telefono, contrasena))
            get_db().commit()
            
            # Obtener el ID del usuario recién creado
            id_usuario = cursor.lastrowid
            
            # Asignar rol al usuario
            cursor.execute("SELECT IDRol FROM Rol WHERE Nombre = %s", (rol,))
            id_rol = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO UsuarioRol (IDUsuario, IDRol)
                VALUES (%s, %s)
            """, (id_usuario, id_rol))
            get_db().commit()
            
            flash('Usuario registrado exitosamente', 'success')
            return redirect(url_for('gestion_usuarios'))
            
        except Exception as e:
            get_db().rollback()
            flash(f'Error al registrar usuario: {str(e)}', 'error')
            return redirect(url_for('gestion_usuarios'))
    
    # Obtener lista de usuarios con sus roles
    cursor = get_db().cursor()
    cursor.execute("""
        SELECT u.*, GROUP_CONCAT(r.Nombre) as roles
        FROM Usuario u
        LEFT JOIN UsuarioRol ur ON u.IDUsuario = ur.IDUsuario
        LEFT JOIN Rol r ON ur.IDRol = r.IDRol
        GROUP BY u.IDUsuario
    """)
    usuarios = cursor.fetchall()
    
    # Obtener lista de roles disponibles
    cursor.execute("SELECT * FROM Rol")
    roles = cursor.fetchall()
    
    return render_template('registro_usuario.html', usuarios=usuarios, roles=roles)

# Expresión regular para validar la contraseña
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z]).{8,}$')

# Ruta para la página de inicio
@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/inicio')
def inicio_redirect():
    return redirect(url_for('inicio'))

# Ruta para la página de inicio
@app.route('/principal')
def principal():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))
    
    # Obtener las últimas sugerencias para mostrar en la página principal
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('''
            SELECT s.*, e.Descripcion as EstadoDescripcion 
            FROM sugerencias s
            LEFT JOIN Estado e ON s.Estado = e.IDEstado 
            WHERE s.Estado = 1
            ORDER BY s.Fecha DESC 
            LIMIT 5
        ''')
        sugerencias = cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener sugerencias: {str(e)}")
        sugerencias = []
    finally:
        cursor.close()
        connection.close()
    
    return render_template('principal.html', sugerencias=sugerencias)

@app.route('/insertar_ceiba')
def insertar_ceiba():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Primero verificar si ya existe la ceiba
        cursor.execute('SELECT IDArbol FROM Arbol WHERE NombreCientifico = %s', ('Ceiba pentandra',))
        if cursor.fetchone():
            flash('La ceiba ya existe en la base de datos', 'info')
            return redirect(url_for('principal'))

        # Insertar la ceiba
        cursor.execute('''
            INSERT INTO Arbol (
                NombreCientifico, 
                NombreVulgar, 
                UbicacionGeografica, 
                Caracteristicas, 
                ServicioEcosistemico, 
                Cantidad, 
                TipoArbol, 
                UsoArbol, 
                TipoBosque, 
                Centro, 
                Estado
            ) VALUES (
                'Ceiba pentandra',
                'Ceiba',
                'Regiones cálidas de Colombia',
                'Árbol majestuoso que puede alcanzar hasta 70m de altura. Hojas compuestas de 5-9 folíolos.',
                'Sombra, madera, medicina tradicional',
                1,
                1,  -- Asumiendo que 1 es el ID del tipo de árbol nativo
                1,  -- Asumiendo que 1 es el ID del uso ornamental
                1,  -- Asumiendo que 1 es el ID del tipo de bosque tropical
                1,  -- Asumiendo que 1 es el ID del centro principal
                1   -- Estado activo
            )
        ''')
        connection.commit()
        flash('Árbol de ceiba insertado correctamente', 'success')
    except Exception as e:
        print(f"Error al insertar la ceiba: {str(e)}")
        flash(f'Error al insertar la ceiba: {str(e)}', 'error')
    finally:
        cursor.close()
        connection.close()
    return redirect(url_for('principal'))

# Ruta para la página de gestión (sidebar)
@app.route('/gestion')
def gestion():
    if 'usuario' not in session:
        flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
        return redirect(url_for('iniciar_sesion'))
    return render_template('gestion.html')

# Ruta para la página de sidebar (gestión)
@app.route('/sidebar')
def sidebar():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))
    return redirect(url_for('inicio'))

# Ruta para el registro de nuevos usuarios
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        correo = request.form['correo']
        telefono = request.form['telefono']
        contrasena = request.form['contrasena']
        validar_contrasena = request.form['validar_contrasena']

        # Validar que las contraseñas coincidan
        if contrasena != validar_contrasena:
            return jsonify({
                'success': False,
                'message': 'Las contraseñas no coinciden'
            })

        # Validar la contraseña con la expresión regular
        if not PASSWORD_REGEX.match(contrasena):
            return jsonify({
                'success': False,
                'message': 'La contraseña debe tener al menos 8 caracteres y una letra mayúscula'
            })

        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            # Verificar si el correo ya está registrado
            cursor.execute('SELECT * FROM Usuario WHERE CorreoElectronico = %s', (correo,))
            if cursor.fetchone():
                return jsonify({
                    'success': False,
                    'message': 'El correo electrónico ya está registrado'
                })

            # Insertar el nuevo usuario en la base de datos
            cursor.execute('''
                INSERT INTO Usuario (Nombres, Apellidos, CorreoElectronico, Telefono, Contrasena, Estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (nombres, apellidos, correo, telefono, contrasena, 1))  # Estado 1 = Activo
            connection.commit()
            return jsonify({
                'success': True,
                'message': 'Registro exitoso'
            })
        except Exception as e:
            connection.rollback()
            return jsonify({
                'success': False,
                'message': f'Error al registrar el usuario: {str(e)}'
            })
        finally:
            cursor.close()
            connection.close()

    return render_template('registro.html')

# Ruta para la página de inicio de sesión
@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        
        if not correo or not contrasena:
            return jsonify({
                'success': False,
                'message': 'Por favor ingrese correo y contraseña'
            })
        
        cursor = get_db().cursor()
        try:
            # Verificar credenciales y obtener roles
            cursor.execute("""
                SELECT u.*, GROUP_CONCAT(r.Nombre) as roles
                FROM Usuario u
                LEFT JOIN UsuarioRol ur ON u.IDUsuario = ur.IDUsuario
                LEFT JOIN Rol r ON ur.IDRol = r.IDRol
                WHERE u.CorreoElectronico = %s AND u.Contrasena = %s AND u.Estado = 1
                GROUP BY u.IDUsuario
            """, (correo, contrasena))
            usuario = cursor.fetchone()
            
            if usuario:
                # Crear sesión con los roles como lista
                session['usuario'] = {
                    'IDUsuario': usuario['IDUsuario'],
                    'Nombres': usuario['Nombres'],
                    'Apellidos': usuario['Apellidos'],
                    'Correo': usuario['CorreoElectronico'],
                    'roles': usuario['roles'].split(',') if usuario['roles'] else []
                }
                
                return jsonify({
                    'success': True,
                    'message': 'Inicio de sesión exitoso',
                    'redirect': url_for('principal')
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Correo o contraseña incorrectos'
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error al iniciar sesión: {str(e)}'
            })
        finally:
            cursor.close()
    
    return render_template('iniciar_sesion.html')

# Ruta para cerrar sesión
@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('inicio'))

# Ruta para la gestión de árboles
@app.route('/arbol', methods=['GET', 'POST'])
def arbol():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre_cientifico = request.form['nombre_cientifico']
            nombre_vulgar = request.form['nombre_vulgar']
            ubicacion_geografica = request.form['ubicacion_geografica']
            caracteristicas = request.form['caracteristicas']
            servicio_ecosistemico = request.form['servicio_ecosistemico']
            cantidad = request.form['cantidad']
            tipo_arbol = request.form['tipo_arbol']
            uso_arbol = request.form['uso_arbol']
            tipo_bosque = request.form['tipo_bosque']
            centro = request.form['centro']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO Arbol (NombreCientifico, NombreVulgar, UbicacionGeografica, Caracteristicas, 
                ServicioEcosistemico, Cantidad, TipoArbol, UsoArbol, TipoBosque, Centro, Estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (nombre_cientifico, nombre_vulgar, ubicacion_geografica, caracteristicas, 
                  servicio_ecosistemico, cantidad, tipo_arbol, uso_arbol, tipo_bosque, centro, estado))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Árbol registrado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar el árbol: {str(e)}', 'error')
        return redirect(url_for('arbol'))

    # Obtener datos para el formulario
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM TipoArbol')
    tipos_arbol = cursor.fetchall()
    cursor.execute('SELECT * FROM UsoArbol')
    usos_arbol = cursor.fetchall()
    cursor.execute('SELECT * FROM TipoBosque')
    tipos_bosque = cursor.fetchall()
    cursor.execute('SELECT * FROM Centro')
    centros = cursor.fetchall()
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    # Obtener árboles con información descriptiva
    cursor.execute('''
        SELECT 
            a.*,
            ta.NombreCientifico as TipoArbolNombreCientifico,
            ta.NombreVulgar as TipoArbolNombreVulgar,
            ua.Descripcion as UsoArbolDescripcion,
            tb.Descripcion as TipoBosqueDescripcion,
            c.Nombre as CentroNombre,
            e.Descripcion as EstadoDescripcion
        FROM Arbol a
        LEFT JOIN TipoArbol ta ON a.TipoArbol = ta.IDTipoArbol
        LEFT JOIN UsoArbol ua ON a.UsoArbol = ua.IDUso
        LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
        LEFT JOIN Centro c ON a.Centro = c.IDCentro
        LEFT JOIN Estado e ON a.Estado = e.IDEstado
        ORDER BY a.IDArbol DESC
    ''')
    arboles = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('arbol.html', tipos_arbol=tipos_arbol, usos_arbol=usos_arbol, 
                         tipos_bosque=tipos_bosque, centros=centros, estados=estados, arboles=arboles)

@app.route('/arbol/editar/<int:id>', methods=['GET', 'POST'])
def editar_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre_cientifico = request.form['nombre_cientifico']
            nombre_vulgar = request.form['nombre_vulgar']
            ubicacion_geografica = request.form['ubicacion_geografica']
            caracteristicas = request.form['caracteristicas']
            servicio_ecosistemico = request.form['servicio_ecosistemico']
            cantidad = request.form['cantidad']
            tipo_arbol = request.form['tipo_arbol']
            uso_arbol = request.form['uso_arbol']
            tipo_bosque = request.form['tipo_bosque']
            centro = request.form['centro']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE Arbol SET NombreCientifico = %s, NombreVulgar = %s, UbicacionGeografica = %s,
                Caracteristicas = %s, ServicioEcosistemico = %s, Cantidad = %s, TipoArbol = %s,
                UsoArbol = %s, TipoBosque = %s, Centro = %s, Estado = %s
                WHERE IDArbol = %s
            ''', (nombre_cientifico, nombre_vulgar, ubicacion_geografica, caracteristicas,
                  servicio_ecosistemico, cantidad, tipo_arbol, uso_arbol, tipo_bosque, centro, estado, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Árbol actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar el árbol: {str(e)}', 'error')
        return redirect(url_for('arbol'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Arbol WHERE IDArbol = %s', (id,))
    arbol = cursor.fetchone()
    cursor.execute('SELECT * FROM TipoArbol')
    tipos_arbol = cursor.fetchall()
    cursor.execute('SELECT * FROM UsoArbol')
    usos_arbol = cursor.fetchall()
    cursor.execute('SELECT * FROM TipoBosque')
    tipos_bosque = cursor.fetchall()
    cursor.execute('SELECT * FROM Centro')
    centros = cursor.fetchall()
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('editar_arbol.html', arbol=arbol, tipos_arbol=tipos_arbol,
                         usos_arbol=usos_arbol, tipos_bosque=tipos_bosque, centros=centros, estados=estados)

@app.route('/arbol/eliminar/<int:id>')
def eliminar_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Iniciar transacción
        connection.begin()
        
        # 1. Primero establecer a NULL la columna MedidasArbol en la tabla Arbol para romper la referencia circular
        cursor.execute('UPDATE Arbol SET MedidasArbol = NULL WHERE IDArbol = %s', (id,))
        
        # 2. Verificar y eliminar las medidas asociadas al árbol
        cursor.execute('SELECT COUNT(*) as total FROM MedidasArbol WHERE Arbol = %s', (id,))
        result = cursor.fetchone()
        if result and result['total'] > 0:
            # Eliminar las medidas asociadas
            cursor.execute('DELETE FROM MedidasArbol WHERE Arbol = %s', (id,))
            flash(f'Se eliminaron {result["total"]} medidas asociadas al árbol', 'info')
        
        # 3. Verificar si hay QRs asociados al árbol
        try:
            cursor.execute('SELECT COUNT(*) as total FROM CodigoQR WHERE Arbol = %s', (id,))
            result = cursor.fetchone()
            if result and result['total'] > 0:
                # Eliminar los QRs asociados
                cursor.execute('DELETE FROM CodigoQR WHERE Arbol = %s', (id,))
                flash(f'Se eliminaron {result["total"]} códigos QR asociados al árbol', 'info')
        except Exception as qr_error:
            # Si la tabla CodigoQR no existe, continuamos
            pass
        
        # 4. Buscar otras relaciones y establecerlas a NULL
        try:
            # Verificar si otros árboles referencian a este
            cursor.execute('UPDATE Arbol SET TipoArbol = NULL WHERE TipoArbol = %s AND IDArbol != %s', (id, id))
            cursor.execute('UPDATE Arbol SET UsoArbol = NULL WHERE UsoArbol = %s AND IDArbol != %s', (id, id))
        except Exception as rel_error:
            # Continuamos si no hay estas relaciones
            pass
        
        # 5. Finalmente eliminar el árbol
        cursor.execute('DELETE FROM Arbol WHERE IDArbol = %s', (id,))
        
        # Confirmar transacción
        connection.commit()
        cursor.close()
        connection.close()
        flash('Árbol eliminado exitosamente', 'success')
    except Exception as e:
        # Revertir cambios en caso de error
        if 'connection' in locals():
            connection.rollback()
        flash(f'Error al eliminar el árbol: {str(e)}', 'error')
        # Proporcionar más información sobre el error para depuración
        import traceback
        print(traceback.format_exc())
    
    return redirect(url_for('arbol'))

# Ruta para la gestión de centros
@app.route('/centro', methods=['GET', 'POST'])
def centro():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO Centro (Nombre, Descripcion, Estado)
                VALUES (%s, %s, %s)
            ''', (nombre, descripcion, estado))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Centro registrado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar el centro: {str(e)}', 'error')
        return redirect(url_for('centro'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Centro')
    centros = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('centro.html', centros=centros)

# Ruta para editar un centro
@app.route('/centro/editar/<int:id>', methods=['GET', 'POST'])
def editar_centro(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE Centro SET Nombre = %s, Descripcion = %s, Estado = %s
                WHERE IDCentro = %s
            ''', (nombre, descripcion, estado, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Centro actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar el centro: {str(e)}', 'error')
        return redirect(url_for('centro'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Centro WHERE IDCentro = %s', (id,))
    centro = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('editar_centro.html', centro=centro)

# Ruta para eliminar un centro
@app.route('/centro/eliminar/<int:id>')
def eliminar_centro(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Centro WHERE IDCentro = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Centro eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el centro: {str(e)}', 'error')
    return redirect(url_for('centro'))

# Ruta para la gestión de tipos de árbol
@app.route('/tipo_arbol', methods=['GET', 'POST'])
def tipo_arbol():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre_cientifico = request.form['nombre_cientifico']
            nombre_vulgar = request.form['nombre_vulgar']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO TipoArbol (NombreCientifico, NombreVulgar, Estado)
                VALUES (%s, %s, %s)
            ''', (nombre_cientifico, nombre_vulgar, estado))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Tipo de árbol registrado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar el tipo de árbol: {str(e)}', 'error')
        return redirect(url_for('tipo_arbol'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM TipoArbol')
    tipos = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('tipo_arbol.html', tipos=tipos)

# Ruta para editar un tipo de árbol
@app.route('/tipo_arbol/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre_cientifico = request.form['nombre_cientifico']
            nombre_vulgar = request.form['nombre_vulgar']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE TipoArbol SET NombreCientifico = %s, NombreVulgar = %s, Estado = %s
                WHERE IDTipoArbol = %s
            ''', (nombre_cientifico, nombre_vulgar, estado, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Tipo de árbol actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar el tipo de árbol: {str(e)}', 'error')
        return redirect(url_for('tipo_arbol'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM TipoArbol WHERE IDTipoArbol = %s', (id,))
    tipo_arbol = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('editar_tipo_arbol.html', tipo_arbol=tipo_arbol)

# Ruta para eliminar un tipo de árbol
@app.route('/tipo_arbol/eliminar/<int:id>')
def eliminar_tipo_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM TipoArbol WHERE IDTipoArbol = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Tipo de árbol eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el tipo de árbol: {str(e)}', 'error')
    return redirect(url_for('tipo_arbol'))

# Ruta para la gestión de usos de árbol
@app.route('/uso_arbol', methods=['GET', 'POST'])
def uso_arbol():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            descripcion = request.form['descripcion']
            estado = request.form['estado']

            cursor.execute('''
                INSERT INTO UsoArbol (Descripcion, Estado)
                VALUES (%s, %s)
            ''', (descripcion, estado))
            connection.commit()
            flash('Uso de árbol registrado exitosamente', 'success')
        except Exception as e:
            connection.rollback()
            flash(f'Error al registrar el uso de árbol: {str(e)}', 'error')
        finally:
            cursor.close()
            connection.close()
        return redirect(url_for('uso_arbol'))

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('''
            SELECT u.*, e.Descripcion as EstadoDescripcion 
            FROM UsoArbol u 
            LEFT JOIN Estado e ON u.Estado = e.IDEstado 
            ORDER BY u.IDUso DESC
        ''')
        usos = cursor.fetchall()
    except Exception as e:
        flash(f'Error al cargar los usos de árbol: {str(e)}', 'error')
        usos = []
    finally:
        cursor.close()
        connection.close()
    return render_template('uso_arbol.html', usos=usos)

# Ruta para editar un uso de árbol
@app.route('/uso_arbol/editar/<int:id>', methods=['GET', 'POST'])
def editar_uso_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            descripcion = request.form['descripcion']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE UsoArbol SET Descripcion = %s, Estado = %s
                WHERE IDUso = %s
            ''', (descripcion, estado, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Uso de árbol actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar el uso de árbol: {str(e)}', 'error')
        return redirect(url_for('uso_arbol'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM UsoArbol WHERE IDUso = %s', (id,))
    uso_arbol = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('editar_uso_arbol.html', uso_arbol=uso_arbol)

# Ruta para eliminar un uso de árbol
@app.route('/uso_arbol/eliminar/<int:id>')
def eliminar_uso_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM UsoArbol WHERE IDUso = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Uso de árbol eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el uso de árbol: {str(e)}', 'error')
    return redirect(url_for('uso_arbol'))

# Ruta para la gestión de tipos de bosque
@app.route('/tipo_bosque', methods=['GET', 'POST'])
def tipo_bosque():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            descripcion = request.form['descripcion']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO TipoBosque (Descripcion, Estado)
                VALUES (%s, %s)
            ''', (descripcion, estado))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Tipo de bosque registrado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar el tipo de bosque: {str(e)}', 'error')
        return redirect(url_for('tipo_bosque'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM TipoBosque')
    tipos = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('tipo_bosque.html', tipos=tipos)

# Ruta para editar un tipo de bosque
@app.route('/tipo_bosque/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_bosque(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            descripcion = request.form['descripcion']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE TipoBosque SET Descripcion = %s, Estado = %s
                WHERE IDTipoBosque = %s
            ''', (descripcion, estado, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Tipo de bosque actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar el tipo de bosque: {str(e)}', 'error')
        return redirect(url_for('tipo_bosque'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM TipoBosque WHERE IDTipoBosque = %s', (id,))
    tipo_bosque = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('editar_tipo_bosque.html', tipo_bosque=tipo_bosque)

# Ruta para eliminar un tipo de bosque
@app.route('/tipo_bosque/eliminar/<int:id>')
def eliminar_tipo_bosque(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM TipoBosque WHERE IDTipoBosque = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Tipo de bosque eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el tipo de bosque: {str(e)}', 'error')
    return redirect(url_for('tipo_bosque'))

# Ruta para la gestión de medidas de árbol
@app.route('/medidas_arbol', methods=['GET', 'POST'])
def medidas_arbol():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        connection = None
        cursor = None
        try:
            # Obtener los datos del formulario
            arbol = request.form['arbol']
            cap = request.form['cap']
            dap = request.form['dap']
            altura_comercial = request.form['altura_comercial']
            altura_total = request.form['altura_total']
            area_basal = request.form['area_basal']
            estado = request.form['estado']

            # Validar los datos
            if not arbol or not cap or not dap or not altura_comercial or not altura_total or not area_basal or not estado:
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('medidas_arbol'))

            # Convertir a números y validar
            try:
                cap = float(cap)
                dap = float(dap)
                altura_comercial = float(altura_comercial)
                altura_total = float(altura_total)
                area_basal = float(area_basal)
                arbol_id = int(arbol)
                estado_id = int(estado)
            except ValueError:
                flash('Los valores numéricos son inválidos', 'error')
                return redirect(url_for('medidas_arbol'))

            # Establecer la conexión y comenzar la transacción
            connection = get_db_connection()
            cursor = connection.cursor()
            connection.begin()

            # Verificar que el árbol existe
            cursor.execute('SELECT IDArbol FROM Arbol WHERE IDArbol = %s', (arbol_id,))
            arbol_existe = cursor.fetchone()
            if not arbol_existe:
                flash('El árbol seleccionado no existe', 'error')
                return redirect(url_for('medidas_arbol'))

            # Verificar que el estado existe
            cursor.execute('SELECT IDEstado FROM Estado WHERE IDEstado = %s', (estado_id,))
            estado_existe = cursor.fetchone()
            if not estado_existe:
                flash('El estado seleccionado no existe', 'error')
                return redirect(url_for('medidas_arbol'))

            # Insertar las medidas
            insert_query = '''
                INSERT INTO MedidasArbol (Arbol, CAP, DAP, AlturaComercial, AlturaTotal, AreaBasal, Estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (arbol_id, cap, dap, altura_comercial, altura_total, area_basal, estado_id))
            
            # Confirmar la transacción
            connection.commit()
            flash('Medidas de árbol registradas exitosamente', 'success')
            
        except Exception as e:
            # En caso de error, revertir los cambios
            if connection:
                connection.rollback()
            flash(f'Error al registrar las medidas de árbol: {str(e)}', 'error')
            # Imprimir el error completo para depuración
            import traceback
            print(f"Error en medidas_arbol: {str(e)}")
            print(traceback.format_exc())
        finally:
            # Cerrar recursos
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        
        return redirect(url_for('medidas_arbol'))

    # Para solicitudes GET, mostrar el formulario
    try:
        # Obtener árboles activos para el select
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('SELECT IDArbol, NombreCientifico FROM Arbol WHERE Estado = 1')
        arboles = cursor.fetchall()

        # Obtener todas las medidas con información del árbol y estado
        cursor.execute('''
            SELECT 
                m.IDMedida,
                m.CAP,
                m.DAP,
                m.AlturaComercial,
                m.AlturaTotal,
                m.AreaBasal,
                m.Arbol,
                m.Estado,
                a.NombreCientifico,
                e.Descripcion as EstadoDescripcion
            FROM MedidasArbol m 
            LEFT JOIN Arbol a ON m.Arbol = a.IDArbol
            LEFT JOIN Estado e ON m.Estado = e.IDEstado 
            ORDER BY m.IDMedida DESC
        ''')
        medidas = cursor.fetchall()

        # Obtener los estados para el formulario
        cursor.execute('SELECT IDEstado, Descripcion FROM Estado')
        estados = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('medidas_arbol.html', medidas=medidas, arboles=arboles, estados=estados)
    
    except Exception as e:
        flash(f'Error al cargar la página: {str(e)}', 'error')
        return redirect(url_for('gestion'))

# Ruta para editar una medida de árbol
@app.route('/medidas_arbol/editar/<int:id>', methods=['GET', 'POST'])
def editar_medida_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        connection = None
        cursor = None
        try:
            # Obtener los datos del formulario
            arbol = request.form['arbol']
            cap = request.form['cap']
            dap = request.form['dap']
            altura_comercial = request.form['altura_comercial']
            altura_total = request.form['altura_total']
            area_basal = request.form['area_basal']
            estado = request.form['estado']

            # Validar los datos
            if not arbol or not cap or not dap or not altura_comercial or not altura_total or not area_basal or not estado:
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('editar_medida_arbol', id=id))

            # Convertir a números y validar
            try:
                cap = float(cap)
                dap = float(dap)
                altura_comercial = float(altura_comercial)
                altura_total = float(altura_total)
                area_basal = float(area_basal)
                arbol_id = int(arbol)
                estado_id = int(estado)
            except ValueError:
                flash('Los valores numéricos son inválidos', 'error')
                return redirect(url_for('editar_medida_arbol', id=id))

            # Establecer la conexión y comenzar la transacción
            connection = get_db_connection()
            cursor = connection.cursor()
            connection.begin()

            # Actualizar las medidas
            update_query = '''
                UPDATE MedidasArbol SET 
                Arbol = %s, 
                CAP = %s, 
                DAP = %s, 
                AlturaComercial = %s, 
                AlturaTotal = %s, 
                AreaBasal = %s, 
                Estado = %s
                WHERE IDMedida = %s
            '''
            cursor.execute(update_query, (arbol_id, cap, dap, altura_comercial, altura_total, area_basal, estado_id, id))
            
            # Confirmar la transacción
            connection.commit()
            flash('Medidas de árbol actualizadas exitosamente', 'success')
        except Exception as e:
            # En caso de error, revertir los cambios
            if connection:
                connection.rollback()
            flash(f'Error al actualizar las medidas de árbol: {str(e)}', 'error')
            # Imprimir el error completo para depuración
            import traceback
            print(f"Error en editar_medida_arbol: {str(e)}")
            print(traceback.format_exc())
        finally:
            # Cerrar recursos
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        
        return redirect(url_for('medidas_arbol'))

    try:
        # Obtener la medida a editar y los árboles disponibles
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('SELECT * FROM MedidasArbol WHERE IDMedida = %s', (id,))
        medida = cursor.fetchone()
        
        if not medida:
            flash('Medida no encontrada', 'error')
            return redirect(url_for('medidas_arbol'))
        
        cursor.execute('SELECT IDArbol, NombreCientifico FROM Arbol')
        arboles = cursor.fetchall()
        
        # Obtener los estados para el formulario
        cursor.execute('SELECT IDEstado, Descripcion FROM Estado')
        estados = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('editar_medida_arbol.html', medida=medida, arboles=arboles, estados=estados)
    except Exception as e:
        flash(f'Error al cargar la página: {str(e)}', 'error')
        return redirect(url_for('medidas_arbol'))

# Ruta para eliminar una medida de árbol
@app.route('/medidas_arbol/eliminar/<int:id>')
def eliminar_medida_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    connection = None
    cursor = None
    try:
        # Establecer conexión y comenzar transacción
        connection = get_db_connection()
        cursor = connection.cursor()
        connection.begin()
        
        # Verificar si existen relaciones con esta medida antes de eliminar
        cursor.execute('UPDATE Arbol SET MedidasArbol = NULL WHERE MedidasArbol = %s', (id,))
        
        # Eliminar la medida
        cursor.execute('DELETE FROM MedidasArbol WHERE IDMedida = %s', (id,))
        
        # Confirmar cambios
        connection.commit()
        flash('Medidas de árbol eliminadas exitosamente', 'success')
    except Exception as e:
        # Revertir cambios en caso de error
        if connection:
            connection.rollback()
        flash(f'Error al eliminar las medidas de árbol: {str(e)}', 'error')
        # Mostrar el error completo para depuración
        import traceback
        print(f"Error en eliminar_medida_arbol: {str(e)}")
        print(traceback.format_exc())
    finally:
        # Cerrar recursos
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
    return redirect(url_for('medidas_arbol'))

# Ruta para la generación de códigos QR
@app.route('/qr', methods=['GET', 'POST'])
def qr():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            arbol_id = request.form.get('arbol_id')
            tamano = int(request.form.get('tamano', 200))

            if not arbol_id:
                flash('Por favor seleccione un árbol', 'error')
                return redirect(url_for('qr'))

            # Obtener información del árbol
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM Arbol WHERE IDArbol = %s', (arbol_id,))
            arbol = cursor.fetchone()
            cursor.close()
            connection.close()

            if not arbol:
                flash('Árbol no encontrado', 'error')
                return redirect(url_for('qr'))

            # Generar el código QR
            import qrcode
            from io import BytesIO
            import base64

            # Crear la URL del árbol específico
            base_url = request.host_url.rstrip('/')
            arbol_url = f"{base_url}/ver_arbol/{arbol_id}"

            # Crear el QR con la URL del árbol
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(arbol_url)
            qr.make(fit=True)

            # Crear la imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir la imagen a base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qr_data = base64.b64encode(buffered.getvalue()).decode()

            # Obtener la fecha actual
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Obtener la lista de árboles para el formulario
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM Arbol')
            arboles = cursor.fetchall()
            cursor.close()
            connection.close()

            flash('QR generado exitosamente', 'success')
            return render_template('qr.html', 
                                arboles=arboles,
                                qr_data=qr_data,
                                arbol_seleccionado=arbol,
                                fecha_actual=fecha_actual)

        except Exception as e:
            flash(f'Error al generar el QR: {str(e)}', 'error')
            return redirect(url_for('qr'))

    # GET request - mostrar el formulario
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Arbol')
    arboles = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('qr.html', arboles=arboles)

# Ruta para registrar sugerencias desde la página principal
@app.route('/registrar_sugerencia', methods=['POST'])
def registrar_sugerencia():
    if not session.get('usuario'):
        return jsonify({
            'success': False,
            'message': 'Debes iniciar sesión para enviar sugerencias'
        }), 401

    try:
        # Obtener la sugerencia del formulario
        sugerencia = request.form.get('sugerencia')
        
        # Validar que la sugerencia no esté vacía
        if not sugerencia:
            return jsonify({
                'success': False,
                'message': 'El campo sugerencia es requerido'
            }), 400

        # Obtener datos del usuario de la sesión
        nombre = session['usuario']['Nombres']
        email = session['usuario']['CorreoElectronico']

        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            # Insertar la sugerencia
            cursor.execute('''
                INSERT INTO sugerencias (Nombre, Email, Sugerencia, Estado)
                VALUES (%s, %s, %s, %s)
            ''', (nombre, email, sugerencia, 1))
            connection.commit()
            
            # Obtener la fecha actual
            fecha_actual = datetime.now().strftime('%d/%m/%Y')
            
            return jsonify({
                'success': True,
                'message': '¡Gracias por tu sugerencia!',
                'nuevaSugerencia': {
                    'Nombre': nombre,
                    'Fecha': fecha_actual,
                    'Sugerencia': sugerencia
                }
            })
            
        except Exception as db_error:
            connection.rollback()
            return jsonify({
                'success': False,
                'message': f'Error al guardar en la base de datos: {str(db_error)}'
            }), 500
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error al procesar la sugerencia. Por favor, intenta nuevamente.'
        }), 500

# Ruta para la gestión de sugerencias
@app.route('/sugerencias', methods=['GET', 'POST'])
def sugerencias():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            email = request.form['email']
            sugerencia = request.form['sugerencia']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO sugerencias (Nombre, Email, Sugerencia, Estado)
                VALUES (%s, %s, %s, %s)
            ''', (nombre, email, sugerencia, estado))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Sugerencia registrada exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar la sugerencia: {str(e)}', 'error')
        return redirect(url_for('sugerencias'))

    # Obtener todas las sugerencias y estados para mostrar en la tabla
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Obtener los estados para el formulario
        cursor.execute('SELECT * FROM Estado')
        estados = cursor.fetchall()
        
        # Obtener todas las sugerencias con su estado
        cursor.execute('''
            SELECT s.*, e.Descripcion as EstadoDescripcion 
            FROM sugerencias s
            LEFT JOIN Estado e ON s.Estado = e.IDEstado 
            ORDER BY s.Fecha DESC
        ''')
        sugerencias = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error al obtener las sugerencias: {str(e)}', 'error')
        sugerencias = []
        estados = []
    finally:
        cursor.close()
        connection.close()

    return render_template('sugerencias.html', sugerencias=sugerencias, estados=estados)

# Ruta para eliminar una sugerencia
@app.route('/sugerencias/eliminar/<int:id>')
def eliminar_sugerencia(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM sugerencias WHERE IDSugerencia = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Sugerencia eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la sugerencia: {str(e)}', 'error')
    return redirect(url_for('sugerencias'))

# Ruta para actualizar el estado de una sugerencia
@app.route('/sugerencias/actualizar_estado/<int:id>', methods=['POST'])
def actualizar_estado_sugerencia(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        nuevo_estado = request.form['estado']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE sugerencias SET Estado = %s
            WHERE IDSugerencia = %s
        ''', (nuevo_estado, id))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Estado de la sugerencia actualizado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al actualizar el estado de la sugerencia: {str(e)}', 'error')
    return redirect(url_for('sugerencias'))

# Ruta para la gestión de perfil
@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))
    
    connection = None
    try:
        if request.method == 'POST':
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            telefono = request.form['telefono']
            correo = request.form['correo']
            
            connection = get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute('''
                    UPDATE Usuario 
                    SET Nombres = %s, Apellidos = %s, Telefono = %s, CorreoElectronico = %s
                    WHERE IDUsuario = %s
                ''', (nombres, apellidos, telefono, correo, session['usuario']['IDUsuario']))
                connection.commit()
            
            # Actualizar datos en la sesión solo después de la actualización exitosa
            session['usuario']['Nombres'] = nombres
            session['usuario']['Apellidos'] = apellidos
            session['usuario']['Telefono'] = telefono
            session['usuario']['CorreoElectronico'] = correo
            
            flash('Perfil actualizado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al actualizar el perfil: {str(e)}', 'error')
    finally:
        if connection:
            connection.close()
    
    return render_template('perfil.html')

# Ruta para cambiar contraseña
@app.route('/cambiar_contrasena', methods=['POST'])
def cambiar_contrasena():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))
    
    try:
        contrasena_actual = request.form['contrasena_actual']
        nueva_contrasena = request.form['nueva_contrasena']
        confirmar_contrasena = request.form['confirmar_contrasena']
        
        if nueva_contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('perfil'))
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT Contrasena FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
        usuario = cursor.fetchone()

        if usuario['Contrasena'] != contrasena_actual:
            flash('La contraseña actual es incorrecta', 'error')
            cursor.close()
            connection.close()
            return redirect(url_for('perfil'))
        
        cursor.execute('''
            UPDATE Usuario SET Contrasena = %s
            WHERE IDUsuario = %s
        ''', (nueva_contrasena, session['usuario']['IDUsuario']))
        connection.commit()
        cursor.close()
        connection.close()
        
        flash('Contraseña actualizada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al cambiar la contraseña: {str(e)}', 'error')
    return redirect(url_for('perfil'))

# Ruta para eliminar cuenta
@app.route('/eliminar_cuenta', methods=['POST'])
def eliminar_cuenta():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))
    
    try:
        contrasena = request.form['contrasena']
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT Contrasena FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
        usuario = cursor.fetchone()
        
        if usuario['Contrasena'] != contrasena:
            flash('Contraseña incorrecta', 'error')
            cursor.close()
            connection.close()
            return redirect(url_for('perfil'))
        
        cursor.execute('DELETE FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
        connection.commit()
        cursor.close()
        connection.close()

        session.clear()
        flash('Cuenta eliminada exitosamente', 'success')
        return redirect(url_for('inicio'))
    except Exception as e:
        flash(f'Error al eliminar la cuenta: {str(e)}', 'error')
        return redirect(url_for('perfil'))
    
@app.route('/ver_arbol/<int:id>')
def ver_arbol(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        # Obtener información detallada del árbol con sus relaciones
        cursor.execute('''
            SELECT 
                a.*,
                ta.NombreCientifico as TipoArbolNombreCientifico,
                ta.NombreVulgar as TipoArbolNombreVulgar,
                ua.Descripcion as UsoArbolDescripcion,
                tb.Descripcion as TipoBosqueDescripcion,
                c.Nombre as CentroNombre,
                e.Descripcion as EstadoDescripcion
            FROM Arbol a
            LEFT JOIN TipoArbol ta ON a.TipoArbol = ta.IDTipoArbol
            LEFT JOIN UsoArbol ua ON a.UsoArbol = ua.IDUso
            LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
            LEFT JOIN Centro c ON a.Centro = c.IDCentro
            LEFT JOIN Estado e ON a.Estado = e.IDEstado
            WHERE a.IDArbol = %s
        ''', (id,))
        arbol = cursor.fetchone()
        cursor.close()
        connection.close()

        if not arbol:
            flash('Árbol no encontrado', 'error')
            return redirect(url_for('principal'))

        return render_template('ver_arbol.html', arbol=arbol)
    except Exception as e:
        flash(f'Error al cargar el árbol: {str(e)}', 'error')
        return redirect(url_for('principal'))
    
# Ruta para editar usuario
@app.route('/usuario/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))
    
    cursor = get_db().cursor()
    
    if request.method == 'POST':
        try:
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            correo = request.form['correo']
            telefono = request.form['telefono']
            rol = request.form.get('rol', 'Usuario')  # Por defecto es Usuario
            
            # Verificar si el correo ya existe (excluyendo el usuario actual)
            cursor.execute("""
                SELECT IDUsuario FROM Usuario 
                WHERE CorreoElectronico = %s AND IDUsuario != %s
            """, (correo, id))
            if cursor.fetchone():
                flash('El correo electrónico ya está registrado', 'error')
                return redirect(url_for('editar_usuario', id=id))
            
            # Actualizar datos del usuario
            cursor.execute("""
                UPDATE Usuario 
                SET Nombres = %s, Apellidos = %s, CorreoElectronico = %s, Telefono = %s
                WHERE IDUsuario = %s
            """, (nombres, apellidos, correo, telefono, id))
            
            # Actualizar rol del usuario
            cursor.execute("SELECT IDRol FROM rol WHERE Nombre = %s", (rol,))
            resultado = cursor.fetchone()
            if resultado:
                id_rol = resultado['IDRol']
                
                # Verificar si ya existe un rol para este usuario
                cursor.execute("SELECT COUNT(*) as count FROM UsuarioRol WHERE IDUsuario = %s", (id,))
                existe_rol = cursor.fetchone()['count'] > 0
                
                if existe_rol:
                    # Actualizar el rol existente
                    cursor.execute("UPDATE UsuarioRol SET IDRol = %s WHERE IDUsuario = %s", (id_rol, id))
                else:
                    # Insertar nuevo rol
                    cursor.execute("INSERT INTO UsuarioRol (IDUsuario, IDRol) VALUES (%s, %s)", (id, id_rol))
            
            get_db().commit()
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('gestion_usuarios'))
            
        except Exception as e:
            get_db().rollback()
            flash(f'Error al actualizar usuario: {str(e)}', 'error')
            return redirect(url_for('editar_usuario', id=id))
    
    # Obtener datos del usuario
    cursor.execute("""
        SELECT u.*, r.Nombre as rol_actual
        FROM Usuario u
        LEFT JOIN UsuarioRol ur ON u.IDUsuario = ur.IDUsuario
        LEFT JOIN rol r ON ur.IDRol = r.IDRol
        WHERE u.IDUsuario = %s
    """, (id,))
    usuario = cursor.fetchone()
    
    # Obtener lista de roles disponibles
    cursor.execute("SELECT * FROM rol")
    roles = cursor.fetchall()
    
    return render_template('editar_usuario.html', usuario=usuario, roles=roles)

# Ruta para eliminar usuario
@app.route('/usuario/eliminar/<int:id>', methods=['GET', 'POST'])
def eliminar_usuario(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))
    
    # Verificar si el usuario tiene rol de administrador
    cursor = get_db().cursor()
    cursor.execute("""
        SELECT r.Nombre 
        FROM UsuarioRol ur 
        JOIN Rol r ON ur.IDRol = r.IDRol 
        WHERE ur.IDUsuario = %s AND r.Nombre = 'Administrador'
    """, (session['usuario']['IDUsuario'],))
    es_admin = cursor.fetchone() is not None
    
    # Si es una solicitud GET, vamos a mostrar una confirmación o redirigir directamente
    if request.method == 'GET':
        return redirect(url_for('gestion_usuarios'))
    
    # Verificar si el usuario intenta eliminarse a sí mismo
    if id == session['usuario']['IDUsuario']:
        flash('No puede eliminarse a sí mismo', 'error')
        return redirect(url_for('gestion_usuarios'))
    
    try:
        # Eliminar roles del usuario
        cursor.execute("DELETE FROM UsuarioRol WHERE IDUsuario = %s", (id,))
        
        # Eliminar el usuario
        cursor.execute("DELETE FROM Usuario WHERE IDUsuario = %s", (id,))
        
        get_db().commit()
        flash('Usuario eliminado exitosamente', 'success')
        
    except Exception as e:
        get_db().rollback()
        flash(f'Error al eliminar usuario: {str(e)}', 'error')
    
    return redirect(url_for('gestion_usuarios'))
    
if __name__ == '__main__':
    app.run(debug=True)  # ← Correcto: indentado con 4 espacios