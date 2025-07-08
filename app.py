from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, g
from flask_mail import Mail, Message
import pymysql
import os
import qrcode
import io
import base64
from datetime import datetime, timedelta
import re
import json
import random
import string

# Cargar variables de entorno desde .env si existe
try:
    from dotenv import load_dotenv
    import os
    # Cargar el .env desde el directorio del script
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path)
except ImportError:
    # Si python-dotenv no está instalado, continuar sin él
    pass

app = Flask(__name__)

# Función para obtener la URL base correcta
def get_base_url():
    """
    Obtiene la URL base correcta basándose en la request actual.
    Detecta automáticamente desde dónde se está accediendo (localhost, túnel, dominio propio).
    """
    # 1. Verificar headers de proxy/túnel comunes primero
    # X-Forwarded-Host: usado por proxies y túneles
    forwarded_host = request.headers.get('X-Forwarded-Host')
    if forwarded_host:
        # Verificar si también hay X-Forwarded-Proto para el esquema
        forwarded_proto = request.headers.get('X-Forwarded-Proto', 'https')
        return f"{forwarded_proto}://{forwarded_host}"

    # X-Original-Host: usado por algunos túneles
    original_host = request.headers.get('X-Original-Host')
    if original_host:
        return f"https://{original_host}"

    # 2. Usar la URL de la request actual (funciona para localhost, túneles y dominios)
    return request.host_url.rstrip('/')

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'verdeqr.app@gmail.com'  # Cambia esto por tu correo real
app.config['MAIL_PASSWORD'] = 'clave_de_aplicacion'  # Cambia esto por tu clave de aplicación real
app.config['MAIL_DEFAULT_SENDER'] = 'verdeqr.app@gmail.com'  # Cambia esto por tu correo real

# Para pruebas, podemos desactivar el envío real de correos
app.config['MAIL_SUPPRESS_SEND'] = True  # Comentar esta línea en producción

mail = Mail(app)

# Función para generar un token aleatorio
def generar_token(longitud=6):
    return ''.join(random.choices(string.digits, k=longitud))

# Función para limpiar caracteres problemáticos
def limpiar_texto_utf8(texto):
    """
    Limpia caracteres problemáticos que pueden causar errores de codificación
    """
    if not texto:
        return texto

    # Reemplazar caracteres problemáticos comunes
    replacements = {
        '₂': '2',  # Subscript 2
        '₃': '3',  # Subscript 3
        '₄': '4',  # Subscript 4
        '₁': '1',  # Subscript 1
        '²': '2',  # Superscript 2
        '³': '3',  # Superscript 3
        '°': 'º',  # Degree symbol
        '–': '-',  # En dash
        '—': '-',  # Em dash
        ''': "'",  # Left single quotation mark
        ''': "'",  # Right single quotation mark
        '"': '"',  # Left double quotation mark
        '"': '"',  # Right double quotation mark
    }

    for old_char, new_char in replacements.items():
        texto = texto.replace(old_char, new_char)

    # Codificar y decodificar para eliminar caracteres problemáticos
    try:
        texto = texto.encode('utf-8', errors='ignore').decode('utf-8')
    except:
        pass

    return texto

# Función para determinar el género probable basado en el nombre
def determinar_genero(nombre):
    # Lista de terminaciones comunes para nombres femeninos en español
    terminaciones_femeninas = ['a', 'ia', 'na', 'ina', 'ita', 'ela', 'isa', 'esa']
    # Excepciones: nombres masculinos que terminan con 'a'
    excepciones_masculinas = ['juan', 'josue', 'matias', 'elias', 'tobias', 'lucas', 'tomas', 'nicolas', 'jesus']

    # Convertir a minúsculas para comparación
    nombre_lower = nombre.lower()

    # Verificar excepciones primero
    if nombre_lower in excepciones_masculinas:
        return 'masculino'

    # Verificar terminaciones femeninas
    for terminacion in terminaciones_femeninas:
        if nombre_lower.endswith(terminacion):
            return 'femenino'

    # Por defecto, asumir masculino
    return 'masculino'

# Función para obtener el avatar predeterminado según el género
def obtener_avatar_predeterminado(nombre):
    genero = determinar_genero(nombre)

    # Devolver la ruta a la imagen del avatar predeterminado
    if genero == 'femenino':
        return 'css/js/img/avatarf.jpg'
    else:
        return 'css/js/img/avatarm.jpg'
# Configuración usando variables de entorno (Railway/producción) o valores por defecto (local)
app.secret_key = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui_para_desarrollo')

# Configuración de la base de datos usando variables de entorno
def get_db_config():
    # Si tenemos DATABASE_URL (Railway), usarla
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Parsear URL: mysql://user:password@host:port/database
        import re
        match = re.match(r'mysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', database_url)
        if match:
            user, password, host, port, database = match.groups()
            return {
                'host': host,
                'user': user,
                'password': password,
                'database': database,
                'port': int(port),
                'charset': 'utf8mb4',
                'cursorclass': pymysql.cursors.DictCursor
            }

    # Si no, usar variables separadas (local)
    return {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'database': os.environ.get('DB_NAME', 'VerdeQR'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

DB_CONFIG = get_db_config()

# Función para obtener la conexión a la base de datos
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(**DB_CONFIG)
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
            correo = request.form['correo']
            telefono = request.form['telefono']
            contrasena = request.form['contrasena']
            rol = request.form['rol']

            # Verificar si el correo ya existe
            cursor = get_db().cursor()
            cursor.execute("SELECT IDUsuario FROM Usuario WHERE Correo = %s", (correo,))
            if cursor.fetchone():
                flash('El correo electrónico ya está registrado', 'error')
                return redirect(url_for('gestion_usuarios'))

            # Insertar nuevo usuario
            cursor.execute("""
                INSERT INTO Usuario (Nombre, Correo, Telefono, Contraseña, Estado)
                VALUES (%s, %s, %s, %s, 1)
            """, (nombres, correo, telefono, contrasena))
            get_db().commit()

            # Obtener el ID del usuario recién creado
            id_usuario = cursor.lastrowid

            # Asignar rol al usuario
            cursor.execute("SELECT IDRol FROM Rol WHERE NombreRol = %s", (rol,))
            id_rol = cursor.fetchone()['IDRol']
            cursor.execute("""
                INSERT INTO UsuarioRol (Usuario, Rol)
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
        SELECT u.*, GROUP_CONCAT(r.NombreRol) as roles
        FROM Usuario u
        LEFT JOIN UsuarioRol ur ON u.IDUsuario = ur.Usuario
        LEFT JOIN Rol r ON ur.Rol = r.IDRol
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
    # Obtener los árboles, especies y centros para mostrar en la página de inicio
    connection = get_db_connection()
    cursor = connection.cursor()
    arboles_populares = []
    especies_destacadas = []
    centros = []

    try:
        # Obtener los primeros 8 árboles registrados (en orden de registro)
        cursor.execute('''
            SELECT
                a.*,
                e.NombreCientifico as NombreCientifico,
                e.NombreVulgar as NombreVulgar,
                c.NombreCentro as NombreCentro,
                tb.Nombre as TipoBosqueNombre
            FROM Arbol a
            LEFT JOIN Especie e ON a.Especie = e.IDEspecie
            LEFT JOIN Centro c ON a.Centro = c.IDCentro
            LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
            WHERE a.Estado = 1
            ORDER BY a.IDArbol ASC
            LIMIT 8
        ''')
        arboles_populares = cursor.fetchall()

        # Imprimir información de depuración
        print(f"Número de árboles populares encontrados: {len(arboles_populares)}")

        # Corregir las rutas de las imágenes para que usen barras normales
        for arbol in arboles_populares:
            if arbol.get('Imagen'):
                # Reemplazar barras invertidas por barras normales
                arbol['Imagen'] = arbol['Imagen'].replace('\\', '/')

        # Obtener todas las especies (hasta 6)
        cursor.execute('''
            SELECT e.*,
                   (SELECT COUNT(*) FROM Arbol a WHERE a.Especie = e.IDEspecie) as NumArboles
            FROM Especie e
            WHERE e.Estado = 1
            ORDER BY NumArboles DESC, e.NombreVulgar ASC
            LIMIT 6
        ''')
        especies_destacadas = cursor.fetchall()

        # Imprimir información de depuración
        print(f"Número de especies encontradas: {len(especies_destacadas)}")
        for especie in especies_destacadas:
            print(f"Especie: {especie['NombreVulgar']} (ID: {especie['IDEspecie']})")

        # Obtener usos para cada especie
        for especie in especies_destacadas:
            cursor.execute('''
                SELECT
                    ua.Categoria as TipoUso
                FROM UsoArbol ua
                WHERE ua.Especie = %s AND ua.Estado = 1
                GROUP BY ua.Categoria
            ''', (especie['IDEspecie'],))
            usos = cursor.fetchall()
            especie['Usos'] = [uso['TipoUso'] for uso in usos] if usos else []

        # Obtener los centros con árboles registrados
        cursor.execute('''
            SELECT
                c.*,
                COUNT(a.IDArbol) as NumeroArboles
            FROM Centro c
            LEFT JOIN Arbol a ON c.IDCentro = a.Centro
            WHERE c.Estado = 1
            GROUP BY c.IDCentro
            ORDER BY NumeroArboles DESC
            LIMIT 4
        ''')
        centros = cursor.fetchall()

        # Imprimir información de depuración
        print(f"Número de centros encontrados: {len(centros)}")
        for centro in centros:
            print(f"Centro: {centro['NombreCentro']} (ID: {centro['IDCentro']})")

    except Exception as e:
        print(f"Error al obtener datos para la página de inicio: {str(e)}")
        arboles_populares = []
        especies_destacadas = []
        centros = []
    finally:
        cursor.close()
        connection.close()

    return render_template('inicio.html', arboles_populares=arboles_populares, especies_destacadas=especies_destacadas, centros=centros)

@app.route('/inicio')
def inicio_redirect():
    return redirect(url_for('inicio'))

@app.route('/index')
def index():
    return render_template('index.html')

# Ruta para buscar árboles
@app.route('/buscar_arbol')
def buscar_arbol():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para buscar árboles', 'error')
        return redirect(url_for('iniciar_sesion'))

    query = request.args.get('q', '')
    especie_id = request.args.get('especie_id')
    centro_id = request.args.get('centro_id')

    if not query and not especie_id and not centro_id:
        return redirect(url_for('principal'))

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Si se proporciona un ID de especie, buscar árboles de esa especie
        if especie_id:
            cursor.execute('''
                SELECT
                    a.*,
                    e.NombreCientifico as EspecieNombreCientifico,
                    e.NombreVulgar as EspecieNombreVulgar,
                    c.NombreCentro as CentroNombre,
                    tb.Nombre as TipoBosqueNombre
                FROM Arbol a
                LEFT JOIN Especie e ON a.Especie = e.IDEspecie
                LEFT JOIN Centro c ON a.Centro = c.IDCentro
                LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
                WHERE a.Estado = 1 AND a.Especie = %s
                ORDER BY a.IDArbol DESC
            ''', (especie_id,))
            arboles = cursor.fetchall()

            # Obtener información de la especie para mostrar en los resultados
            cursor.execute('SELECT * FROM Especie WHERE IDEspecie = %s', (especie_id,))
            especie_info = cursor.fetchone()
            if especie_info:
                query = f"{especie_info['NombreVulgar']} ({especie_info['NombreCientifico']})"

        # Si se proporciona un ID de centro, buscar árboles de ese centro
        elif centro_id:
            cursor.execute('''
                SELECT
                    a.*,
                    e.NombreCientifico as EspecieNombreCientifico,
                    e.NombreVulgar as EspecieNombreVulgar,
                    c.NombreCentro as CentroNombre,
                    tb.Nombre as TipoBosqueNombre
                FROM Arbol a
                LEFT JOIN Especie e ON a.Especie = e.IDEspecie
                LEFT JOIN Centro c ON a.Centro = c.IDCentro
                LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
                WHERE a.Estado = 1 AND a.Centro = %s
                ORDER BY a.IDArbol DESC
            ''', (centro_id,))
            arboles = cursor.fetchall()

            # Obtener información del centro para mostrar en los resultados
            cursor.execute('SELECT * FROM Centro WHERE IDCentro = %s', (centro_id,))
            centro_info = cursor.fetchone()
            if centro_info:
                query = f"Centro: {centro_info['NombreCentro']}"

        # Si se proporciona una consulta de búsqueda, buscar árboles que coincidan
        elif query:
            cursor.execute('''
                SELECT
                    a.*,
                    e.NombreCientifico as EspecieNombreCientifico,
                    e.NombreVulgar as EspecieNombreVulgar,
                    c.NombreCentro as CentroNombre,
                    tb.Nombre as TipoBosqueNombre
                FROM Arbol a
                LEFT JOIN Especie e ON a.Especie = e.IDEspecie
                LEFT JOIN Centro c ON a.Centro = c.IDCentro
                LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
                WHERE a.Estado = 1 AND (
                    e.NombreCientifico LIKE %s OR
                    e.NombreVulgar LIKE %s OR
                    a.Caracteristicas LIKE %s OR
                    a.ServiciosEcosistemicos LIKE %s OR
                    a.Descripcion LIKE %s OR
                    tb.Nombre LIKE %s OR
                    c.NombreCentro LIKE %s
                )
                ORDER BY a.IDArbol DESC
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
            arboles = cursor.fetchall()

        # Si no hay resultados exactos, buscar resultados similares
        if not arboles:
            # Buscar con términos parciales
            palabras = query.split()
            condiciones = []
            parametros = []

            for palabra in palabras:
                if len(palabra) > 3:  # Solo considerar palabras con más de 3 caracteres
                    condiciones.append("e.NombreCientifico LIKE %s OR e.NombreVulgar LIKE %s OR a.Descripcion LIKE %s")
                    parametros.extend([f'%{palabra}%', f'%{palabra}%', f'%{palabra}%'])

            if condiciones:
                sql_query = f'''
                    SELECT
                        a.*,
                        e.NombreCientifico as EspecieNombreCientifico,
                        e.NombreVulgar as EspecieNombreVulgar,
                        c.NombreCentro as CentroNombre,
                        tb.Nombre as TipoBosqueNombre
                    FROM Arbol a
                    LEFT JOIN Especie e ON a.Especie = e.IDEspecie
                    LEFT JOIN Centro c ON a.Centro = c.IDCentro
                    LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
                    WHERE a.Estado = 1 AND ({" OR ".join(condiciones)})
                    ORDER BY a.IDArbol DESC
                '''
                cursor.execute(sql_query, parametros)
                arboles = cursor.fetchall()

        # Corregir las rutas de las imágenes
        for arbol in arboles:
            if arbol.get('Imagen'):
                arbol['Imagen'] = arbol['Imagen'].replace('\\', '/')
    except Exception as e:
        print(f"Error al buscar árboles: {str(e)}")
        arboles = []
    finally:
        cursor.close()
        connection.close()

    return render_template('resultados_busqueda.html', arboles=arboles, query=query)

# Ruta para mostrar todos los árboles con paginación
@app.route('/todos_los_arboles')
def todos_los_arboles():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    # Obtener el número de página de la URL (por defecto página 1)
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 5 arriba y 5 abajo = 10 por página

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Contar el total de árboles activos
        cursor.execute('SELECT COUNT(*) as total FROM Arbol WHERE Estado = 1')
        total_arboles = cursor.fetchone()['total']

        # Calcular offset para la paginación
        offset = (page - 1) * per_page

        # Obtener árboles con paginación
        cursor.execute('''
            SELECT
                a.*,
                e.NombreCientifico as EspecieNombreCientifico,
                e.NombreVulgar as EspecieNombreVulgar,
                c.NombreCentro as CentroNombre
            FROM Arbol a
            LEFT JOIN Especie e ON a.Especie = e.IDEspecie
            LEFT JOIN Centro c ON a.Centro = c.IDCentro
            WHERE a.Estado = 1
            ORDER BY a.IDArbol DESC
            LIMIT %s OFFSET %s
        ''', (per_page, offset))
        arboles = cursor.fetchall()

        # Corregir las rutas de las imágenes
        for arbol in arboles:
            if arbol.get('Imagen'):
                arbol['Imagen'] = arbol['Imagen'].replace('\\', '/')

        # Calcular información de paginación
        total_pages = (total_arboles + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages

        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': total_arboles,
            'total_pages': total_pages,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_num': page - 1 if has_prev else None,
            'next_num': page + 1 if has_next else None
        }

    except Exception as e:
        print(f"Error al obtener todos los árboles: {str(e)}")
        arboles = []
        pagination_info = {
            'page': 1,
            'per_page': per_page,
            'total': 0,
            'total_pages': 0,
            'has_prev': False,
            'has_next': False,
            'prev_num': None,
            'next_num': None
        }
    finally:
        cursor.close()
        connection.close()

    return render_template('todos_los_arboles.html', arboles=arboles, pagination=pagination_info)

# Ruta para la página principal
@app.route('/principal')
def principal():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    # Actualizar automáticamente las sugerencias antiguas
    actualizar_sugerencias_antiguas()

    connection = get_db_connection()
    cursor = connection.cursor()
    # Inicializar variables con valores predeterminados
    sugerencias = []
    arboles = []
    total_arboles = 0
    total_usuarios = 0
    total_centros = 0

    try:
        # Obtener las últimas sugerencias activas para mostrar en la página principal
        cursor.execute('''
            SELECT s.*, e.NombreEstado as EstadoDescripcion
            FROM sugerencias s
            LEFT JOIN Estado e ON s.Estado = e.IDEstado
            WHERE s.Estado = 1
            ORDER BY s.Fecha DESC
            LIMIT 15
        ''')
        sugerencias = cursor.fetchall()

        # Obtener máximo 12 árboles destacados para mostrar en la página principal
        cursor.execute('''
            SELECT
                a.*,
                e.NombreCientifico as EspecieNombreCientifico,
                e.NombreVulgar as EspecieNombreVulgar,
                c.NombreCentro as CentroNombre
            FROM Arbol a
            LEFT JOIN Especie e ON a.Especie = e.IDEspecie
            LEFT JOIN Centro c ON a.Centro = c.IDCentro
            ORDER BY a.IDArbol DESC
            LIMIT 12
        ''')
        arboles = cursor.fetchall()


        # Obtener estadísticas para la página principal - Usando consultas directas
        cursor.execute('SELECT COUNT(*) as total FROM Arbol')
        total_arboles = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) as total FROM Usuario WHERE Estado = 1')
        total_usuarios = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) as total FROM Centro WHERE Estado = 1')
        total_centros = cursor.fetchone()['total']

        # Corregir las rutas de las imágenes para que usen barras normales
        for arbol in arboles:
            if arbol.get('Imagen'):
                # Reemplazar barras invertidas por barras normales
                arbol['Imagen'] = arbol['Imagen'].replace('\\', '/')


    except Exception as e:
        print(f"Error al obtener datos para la página principal: {str(e)}")
        sugerencias = []
        arboles = []
        total_arboles = 0
        total_usuarios = 0
        total_centros = 0
    finally:
        cursor.close()
        connection.close()


    # Usar los valores reales de la base de datos
    return render_template('principal.html', sugerencias=sugerencias, arboles=arboles,
                           total_arboles=total_arboles, total_usuarios=total_usuarios, total_centros=total_centros)



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
            cursor.execute('SELECT * FROM Usuario WHERE Correo = %s', (correo,))
            if cursor.fetchone():
                return jsonify({
                    'success': False,
                    'message': 'El correo electrónico ya está registrado'
                })

            # Determinar el avatar predeterminado basado en el nombre
            avatar_predeterminado = obtener_avatar_predeterminado(nombres)

            # Insertar el nuevo usuario en la base de datos con avatar predeterminado
            cursor.execute('''
                INSERT INTO Usuario (Nombre, Correo, Telefono, Contraseña, Estado, Imagen)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (nombres + ' ' + apellidos, correo, telefono, contrasena, 1, avatar_predeterminado))  # Estado 1 = Activo
            connection.commit()
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return jsonify({
                'success': True,
                'message': 'Registro exitoso',
                'redirect': url_for('iniciar_sesion')
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
                SELECT u.*, GROUP_CONCAT(r.NombreRol) as roles
                FROM Usuario u
                LEFT JOIN UsuarioRol ur ON u.IDUsuario = ur.Usuario
                LEFT JOIN Rol r ON ur.Rol = r.IDRol
                WHERE u.Correo = %s AND u.Contraseña = %s AND u.Estado = 1
                GROUP BY u.IDUsuario
            """, (correo, contrasena))
            usuario = cursor.fetchone()

            if usuario:
                # Crear sesión con los roles como lista
                # Dividir el nombre completo en nombres y apellidos para mantener compatibilidad
                nombre_completo = usuario['Nombre'] if usuario['Nombre'] else ''
                partes_nombre = nombre_completo.split(' ', 1)
                nombres = partes_nombre[0] if len(partes_nombre) > 0 else ''
                apellidos = partes_nombre[1] if len(partes_nombre) > 1 else ''

                # Si el usuario no tiene imagen, asignar un avatar predeterminado
                imagen_usuario = usuario['Imagen']
                if not imagen_usuario:
                    # Determinar el avatar predeterminado basado en el nombre
                    imagen_usuario = obtener_avatar_predeterminado(nombres)

                    # Actualizar la imagen del usuario en la base de datos
                    try:
                        cursor.execute('UPDATE Usuario SET Imagen = %s WHERE IDUsuario = %s',
                                      (imagen_usuario, usuario['IDUsuario']))
                        get_db().commit()
                    except Exception as e:
                        print(f"Error al actualizar avatar predeterminado: {str(e)}")

                session['usuario'] = {
                    'IDUsuario': usuario['IDUsuario'],
                    'Nombre': nombre_completo,
                    'Nombres': nombres,
                    'Apellidos': apellidos,
                    'Correo': usuario['Correo'],
                    'Telefono': usuario['Telefono'],
                    'Imagen': imagen_usuario,
                    'roles': usuario['roles'].split(',') if usuario['roles'] else []
                }

                # Imprimir información de depuración
                print(f"Sesión de usuario creada: {session['usuario']}")

                # No usar flash aquí porque ya se muestra una notificación modal en el frontend
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
    # Redirigir a inicio con un parámetro para mostrar notificación modal
    return redirect(url_for('inicio', logout_success=1))

# Ruta para olvidar contraseña
@app.route('/olvidar_contrasena', methods=['GET', 'POST'])
def olvidar_contrasena():
    if request.method == 'POST':
        correo = request.form['correo']

        # Verificar si el correo existe en la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT IDUsuario, Nombre FROM Usuario WHERE Correo = %s AND Estado = 1', (correo,))
            usuario = cursor.fetchone()

            if not usuario:
                return jsonify({
                    'success': False,
                    'message': 'No existe una cuenta con este correo electrónico'
                })

            # Generar un token de 6 dígitos
            token = generar_token(6)

            # Calcular la fecha de expiración (30 minutos)
            fecha_expiracion = datetime.now() + timedelta(minutes=30)

            # Guardar el token en la base de datos
            cursor.execute('''
                INSERT INTO tokens_recuperacion (Usuario, Token, FechaExpiracion, Estado)
                VALUES (%s, %s, %s, 1)
            ''', (usuario['IDUsuario'], token, fecha_expiracion))
            connection.commit()

            # Enviar el correo electrónico con el token
            try:
                msg = Message(
                    'Recuperación de contraseña - VerdeQR',
                    recipients=[correo]
                )
                msg.body = f'''Hola {usuario['Nombre']},

Has solicitado restablecer tu contraseña en VerdeQR.

Tu código de verificación es: {token}

Este código expirará en 30 minutos.

Si no solicitaste este cambio, puedes ignorar este correo.

Saludos,
El equipo de VerdeQR
'''
                # Para pruebas, imprimimos el token en la consola
                print(f"TOKEN DE RECUPERACIÓN PARA {correo}: {token}")

                try:
                    mail.send(msg)
                except Exception as e:
                    print(f"Error al enviar correo (ignorado en modo prueba): {str(e)}")

                return jsonify({
                    'success': True,
                    'message': 'Se ha enviado un código de verificación a tu correo electrónico',
                    'redirect': url_for('restablecer_contrasena')
                })
            except Exception as e:
                print(f"Error al enviar el correo: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Error al enviar el correo electrónico. Por favor, intenta nuevamente.'
                })
        except Exception as e:
            connection.rollback()
            print(f"Error en olvidar_contrasena: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error al procesar la solicitud. Por favor, intenta nuevamente.'
            })
        finally:
            cursor.close()
            connection.close()

    return render_template('olvidar_contrasena.html')

# Ruta para restablecer contraseña
@app.route('/restablecer_contrasena', methods=['GET', 'POST'])
def restablecer_contrasena():
    if request.method == 'POST':
        print("Recibida solicitud POST para restablecer contraseña")

        # Verificar si la solicitud es JSON o form-data
        if request.is_json:
            data = request.get_json()
            codigo = data.get('codigo')
            contrasena = data.get('contrasena')
            confirmar_contrasena = data.get('confirmar_contrasena')
        else:
            codigo = request.form.get('codigo')
            contrasena = request.form.get('contrasena')
            confirmar_contrasena = request.form.get('confirmar_contrasena')

        print(f"Código: {codigo}, Contraseña: {contrasena}, Confirmar: {confirmar_contrasena}")

        # Verificar que las contraseñas coincidan
        if contrasena != confirmar_contrasena:
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

        # Verificar que el código sea válido
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Buscar el token en la base de datos
            cursor.execute('''
                SELECT tr.*, u.Correo
                FROM tokens_recuperacion tr
                JOIN Usuario u ON tr.Usuario = u.IDUsuario
                WHERE tr.Token = %s AND tr.Estado = 1 AND tr.FechaExpiracion > NOW()
            ''', (codigo,))
            token_info = cursor.fetchone()

            if not token_info:
                return jsonify({
                    'success': False,
                    'message': 'El código de verificación es inválido o ha expirado'
                })

            # Actualizar la contraseña del usuario
            cursor.execute('''
                UPDATE Usuario
                SET Contraseña = %s
                WHERE IDUsuario = %s
            ''', (contrasena, token_info['Usuario']))

            # Marcar el token como usado
            cursor.execute('''
                UPDATE tokens_recuperacion
                SET Estado = 2
                WHERE IDToken = %s
            ''', (token_info['IDToken'],))

            connection.commit()

            return jsonify({
                'success': True,
                'message': 'Contraseña actualizada exitosamente',
                'redirect': url_for('iniciar_sesion')
            })
        except Exception as e:
            connection.rollback()
            print(f"Error en restablecer_contrasena: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error al procesar la solicitud. Por favor, intenta nuevamente.'
            })
        finally:
            cursor.close()
            connection.close()

    return render_template('restablecer_contrasena.html')

# Ruta para la gestión de árboles
@app.route('/arbol', methods=['GET', 'POST'])
def arbol():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            especie = request.form['especie']
            caracteristicas = request.form['caracteristicas']
            servicios_ecosistemicos = request.form['servicios_ecosistemicos']
            tipo_bosque = request.form['tipo_bosque']
            centro = request.form['centro']
            estado = request.form['estado']
            descripcion = request.form.get('descripcion', '')

            # Procesar la imagen si se ha subido
            imagen_path = None
            if 'imagen' in request.files and request.files['imagen'].filename != '':
                imagen = request.files['imagen']
                # Crear directorio para imágenes si no existe
                upload_folder = os.path.join('static', 'uploads', 'arboles')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                # Guardar la imagen con un nombre único basado en la fecha y el nombre científico
                # Reemplazar espacios y caracteres especiales en el nombre del archivo
                safe_filename = imagen.filename.replace(' ', '_').replace('%', '_').replace('\\', '_').replace('/', '_')
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_filename}"
                # Usar rutas con barras normales para URLs
                imagen_path = 'css/js/img/' + filename  # Guardar en la misma carpeta que las imágenes predefinidas
                imagen_full_path = os.path.join('static', imagen_path.replace('/', os.sep))

                imagen.save(imagen_full_path)

            connection = get_db_connection()
            cursor = connection.cursor()

            # Insertar el árbol con la nueva estructura
            cursor.execute('''
                INSERT INTO Arbol (Especie, Caracteristicas, ServiciosEcosistemicos, TipoBosque, Centro, Imagen, Descripcion, Estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (especie, caracteristicas, servicios_ecosistemicos, tipo_bosque, centro, imagen_path, descripcion, estado))

            connection.commit()
            cursor.close()
            connection.close()
            flash('Árbol registrado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar el árbol: {str(e)}', 'error')
            # Imprimir el error completo para depuración
            import traceback
            print(f"Error en registro de árbol: {str(e)}")
            print(traceback.format_exc())
        return redirect(url_for('arbol'))

    # Obtener datos para el formulario
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Especie WHERE Estado = 1')
    especies = cursor.fetchall()
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
            e.NombreCientifico as EspecieNombreCientifico,
            e.NombreVulgar as EspecieNombreVulgar,
            tb.Nombre as TipoBosqueNombre,
            c.NombreCentro as CentroNombre,
            es.NombreEstado as EstadoNombre
        FROM Arbol a
        LEFT JOIN Especie e ON a.Especie = e.IDEspecie
        LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
        LEFT JOIN Centro c ON a.Centro = c.IDCentro
        LEFT JOIN Estado es ON a.Estado = es.IDEstado
        ORDER BY a.IDArbol DESC
    ''')
    arboles = cursor.fetchall()


    cursor.close()
    connection.close()

    return render_template('arbol.html', especies=especies,
                         tipos_bosque=tipos_bosque, centros=centros, estados=estados, arboles=arboles)

@app.route('/arbol/editar/<int:id>', methods=['GET', 'POST'])
def editar_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            especie = request.form['especie']
            caracteristicas = limpiar_texto_utf8(request.form['caracteristicas'])
            servicios_ecosistemicos = limpiar_texto_utf8(request.form['servicios_ecosistemicos'])
            tipo_bosque = request.form['tipo_bosque']
            centro = request.form['centro']
            estado = request.form['estado']
            descripcion = limpiar_texto_utf8(request.form.get('descripcion', ''))

            # Obtener la imagen actual del árbol
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT Imagen FROM Arbol WHERE IDArbol = %s', (id,))
            arbol_actual = cursor.fetchone()
            imagen_actual = arbol_actual['Imagen'] if arbol_actual else None

            # Procesar la imagen si se ha subido una nueva
            imagen_path = imagen_actual
            if 'imagen' in request.files and request.files['imagen'].filename != '':
                imagen = request.files['imagen']
                # Crear directorio para imágenes si no existe
                upload_folder = os.path.join('static', 'uploads', 'arboles')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                # Guardar la imagen con un nombre único basado en la fecha y el nombre científico
                # Reemplazar espacios y caracteres especiales en el nombre del archivo
                safe_filename = imagen.filename.replace(' ', '_').replace('%', '_').replace('\\', '_').replace('/', '_')
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_filename}"
                # Usar rutas con barras normales para URLs
                imagen_path = 'css/js/img/' + filename  # Guardar en la misma carpeta que las imágenes predefinidas
                imagen_full_path = os.path.join('static', imagen_path.replace('/', os.sep))

                imagen.save(imagen_full_path)

            # Actualizar el árbol con la nueva información
            cursor.execute('''
                UPDATE Arbol SET Especie = %s, Caracteristicas = %s, ServiciosEcosistemicos = %s,
                TipoBosque = %s, Centro = %s, Estado = %s, Imagen = %s, Descripcion = %s
                WHERE IDArbol = %s
            ''', (especie, caracteristicas, servicios_ecosistemicos, tipo_bosque, centro, estado,
                  imagen_path, descripcion, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Árbol actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar el árbol: {str(e)}', 'error')
            # Imprimir el error completo para depuración
            import traceback
            print(f"Error en edición de árbol: {str(e)}")
            print(traceback.format_exc())
        return redirect(url_for('arbol'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT a.*, e.NombreCientifico as EspecieNombreCientifico, e.NombreVulgar as EspecieNombreVulgar
        FROM Arbol a
        LEFT JOIN Especie e ON a.Especie = e.IDEspecie
        WHERE a.IDArbol = %s
    ''', (id,))
    arbol = cursor.fetchone()

    cursor.execute('SELECT * FROM Especie')
    especies = cursor.fetchall()
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
    return render_template('editar_arbol.html', arbol=arbol, especies=especies,
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

        # Verificar y eliminar las medidas asociadas al árbol si la tabla existe
        try:
            cursor.execute('SELECT COUNT(*) as total FROM MedidasArbol WHERE Arbol = %s', (id,))
            result = cursor.fetchone()
            if result and result['total'] > 0:
                # Eliminar las medidas asociadas
                cursor.execute('DELETE FROM MedidasArbol WHERE Arbol = %s', (id,))
                flash(f'Se eliminaron {result["total"]} medidas asociadas al árbol', 'info')
        except Exception as medidas_error:
            # Si la tabla MedidasArbol no existe o hay otro error, continuamos con la eliminación
            print(f"Error al verificar medidas del árbol: {str(medidas_error)}")

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
            direccion = request.form['direccion']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO Centro (NombreCentro, Direccion, Estado)
                VALUES (%s, %s, %s)
            ''', (nombre, direccion, estado))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Centro registrado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar el centro: {str(e)}', 'error')
        return redirect(url_for('centro'))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener centros con información de estado
    cursor.execute('''
        SELECT c.*, e.NombreEstado as EstadoNombre
        FROM Centro c
        LEFT JOIN Estado e ON c.Estado = e.IDEstado
        ORDER BY c.IDCentro DESC
    ''')
    centros = cursor.fetchall()

    # Obtener estados para el formulario
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('centro.html', centros=centros, estados=estados)

# Ruta para editar un centro
@app.route('/centro/editar/<int:id>', methods=['GET', 'POST'])
def editar_centro(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            direccion = request.form['direccion']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE Centro SET NombreCentro = %s, Direccion = %s, Estado = %s
                WHERE IDCentro = %s
            ''', (nombre, direccion, estado, id))
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

    # Obtener estados para el formulario
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('editar_centro.html', centro=centro, estados=estados)

# Ruta para eliminar un centro
@app.route('/centro/eliminar/<int:id>')
def eliminar_centro(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Verificar si el centro está siendo utilizado en árboles
        cursor.execute('SELECT COUNT(*) as total FROM Arbol WHERE Centro = %s', (id,))
        result = cursor.fetchone()
        if result and result['total'] > 0:
            flash(f'No se puede eliminar el centro porque está siendo utilizado en {result["total"]} árboles. Primero debe reasignar o eliminar estos árboles.', 'error')
            return redirect(url_for('centro'))

        # Si no hay árboles asociados, proceder con la eliminación
        cursor.execute('DELETE FROM Centro WHERE IDCentro = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Centro eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el centro: {str(e)}', 'error')
    return redirect(url_for('centro'))

# Ruta para redireccionar tipo_arbol a especie
@app.route('/tipo_arbol', methods=['GET', 'POST'])
def tipo_arbol():
    return redirect(url_for('especie'))

# Ruta para la gestión de especies
@app.route('/especie', methods=['GET', 'POST'])
def especie():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre_cientifico = request.form['nombre_cientifico']
            nombre_vulgar = request.form['nombre_vulgar']
            estado = request.form.get('estado', 1)  # Por defecto activo

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO Especie (NombreCientifico, NombreVulgar, Estado)
                VALUES (%s, %s, %s)
            ''', (nombre_cientifico, nombre_vulgar, estado))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Especie registrada exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar la especie: {str(e)}', 'error')
        return redirect(url_for('especie'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT e.*, es.NombreEstado as EstadoNombre
        FROM Especie e
        LEFT JOIN Estado es ON e.Estado = es.IDEstado
        ORDER BY e.IDEspecie DESC
    ''')
    especies = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('especie.html', especies=especies)

# Ruta para redireccionar editar_tipo_arbol a editar_especie
@app.route('/tipo_arbol/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_arbol(id):
    return redirect(url_for('editar_especie', id=id))

# Ruta para editar una especie
@app.route('/especie/editar/<int:id>', methods=['GET', 'POST'])
def editar_especie(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre_cientifico = request.form['nombre_cientifico']
            nombre_vulgar = request.form['nombre_vulgar']
            estado = request.form.get('estado', 1)  # Por defecto activo

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE Especie SET NombreCientifico = %s, NombreVulgar = %s, Estado = %s
                WHERE IDEspecie = %s
            ''', (nombre_cientifico, nombre_vulgar, estado, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Especie actualizada exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar la especie: {str(e)}', 'error')
        return redirect(url_for('especie'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Especie WHERE IDEspecie = %s', (id,))
    especie_data = cursor.fetchone()

    # Obtener estados para el formulario
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('editar_especie.html', especie=especie_data, estados=estados)

# Ruta para redireccionar eliminar_tipo_arbol a eliminar_especie
@app.route('/tipo_arbol/eliminar/<int:id>')
def eliminar_tipo_arbol(id):
    return redirect(url_for('eliminar_especie', id=id))

# Ruta para eliminar una especie
@app.route('/especie/eliminar/<int:id>')
def eliminar_especie(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Verificar si la especie está siendo utilizada en árboles
        cursor.execute('SELECT COUNT(*) as total FROM Arbol WHERE Especie = %s', (id,))
        result = cursor.fetchone()
        if result and result['total'] > 0:
            flash(f'No se puede eliminar la especie porque está siendo utilizada en {result["total"]} árboles', 'error')
            return redirect(url_for('especie'))

        # Iniciar transacción para eliminar todos los registros relacionados
        connection.begin()

        # Eliminar usos asociados a esta especie
        cursor.execute('SELECT COUNT(*) as total FROM UsoArbol WHERE Especie = %s', (id,))
        result = cursor.fetchone()
        if result and result['total'] > 0:
            cursor.execute('DELETE FROM UsoArbol WHERE Especie = %s', (id,))
            flash(f'Se eliminaron {result["total"]} usos asociados a la especie', 'info')

        # Eliminar curiosidades asociadas a esta especie
        cursor.execute('SELECT COUNT(*) as total FROM CuriosidadesArbol WHERE Especie = %s', (id,))
        result = cursor.fetchone()
        if result and result['total'] > 0:
            cursor.execute('DELETE FROM CuriosidadesArbol WHERE Especie = %s', (id,))
            flash(f'Se eliminaron {result["total"]} curiosidades asociadas a la especie', 'info')

        # Eliminar interacciones ecológicas asociadas a esta especie
        cursor.execute('SELECT COUNT(*) as total FROM InteraccionesEcologicas WHERE Especie = %s', (id,))
        result = cursor.fetchone()
        if result and result['total'] > 0:
            cursor.execute('DELETE FROM InteraccionesEcologicas WHERE Especie = %s', (id,))
            flash(f'Se eliminaron {result["total"]} interacciones ecológicas asociadas a la especie', 'info')

        # Finalmente, eliminar la especie
        cursor.execute('DELETE FROM Especie WHERE IDEspecie = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Especie eliminada exitosamente junto con todos sus registros relacionados', 'success')
    except Exception as e:
        flash(f'Error al eliminar la especie: {str(e)}', 'error')
    return redirect(url_for('especie'))

# Ruta para la gestión de curiosidades
@app.route('/curiosidades', methods=['GET', 'POST'])
def curiosidades():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Obtener especies para el formulario
        cursor.execute('SELECT * FROM Especie')
        especies = cursor.fetchall()

        if request.method == 'POST':
            try:
                especie = request.form['especie']
                descripcion = request.form['descripcion']
                estado = request.form.get('estado', 1)  # Por defecto activo

                cursor.execute('''
                    INSERT INTO CuriosidadesArbol (Especie, Descripcion, Estado)
                    VALUES (%s, %s, %s)
                ''', (especie, descripcion, estado))
                connection.commit()
                flash('Curiosidad registrada exitosamente', 'success')
                return redirect(url_for('curiosidades'))
            except Exception as e:
                flash(f'Error al registrar curiosidad: {str(e)}', 'error')

        # Obtener todas las curiosidades con información de estado
        cursor.execute('''
            SELECT c.*, e.NombreCientifico as EspecieNombre, es.NombreEstado as EstadoNombre
            FROM CuriosidadesArbol c
            LEFT JOIN Especie e ON c.Especie = e.IDEspecie
            LEFT JOIN Estado es ON c.Estado = es.IDEstado
            ORDER BY c.IDCuriosidad DESC
        ''')
        curiosidades_list = cursor.fetchall()

        # Obtener estados para el formulario
        cursor.execute('SELECT * FROM Estado')
        estados = cursor.fetchall()

    except Exception as e:
        flash(f'Error al cargar las curiosidades: {str(e)}', 'error')
        curiosidades_list = []
        especies = []
        estados = []
    finally:
        cursor.close()
        connection.close()

    return render_template('curiosidades.html', curiosidades=curiosidades_list, especies=especies, estados=estados)

# Ruta para editar una curiosidad
@app.route('/curiosidades/editar/<int:id>', methods=['GET', 'POST'])
def editar_curiosidad(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        try:
            especie = request.form['especie']
            descripcion = request.form['descripcion']
            estado = request.form.get('estado', 1)  # Por defecto activo

            cursor.execute('''
                UPDATE CuriosidadesArbol SET Especie = %s, Descripcion = %s, Estado = %s
                WHERE IDCuriosidad = %s
            ''', (especie, descripcion, estado, id))
            connection.commit()
            flash('Curiosidad actualizada exitosamente', 'success')
            return redirect(url_for('curiosidades'))
        except Exception as e:
            flash(f'Error al actualizar curiosidad: {str(e)}', 'error')

    # Obtener especies para el formulario
    cursor.execute('SELECT * FROM Especie')
    especies = cursor.fetchall()

    # Obtener la curiosidad a editar
    cursor.execute('SELECT * FROM CuriosidadesArbol WHERE IDCuriosidad = %s', (id,))
    curiosidad = cursor.fetchone()

    # Obtener estados para el formulario
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()

    if not curiosidad:
        flash('Curiosidad no encontrada', 'error')
        return redirect(url_for('curiosidades'))

    return render_template('editar_curiosidad.html', curiosidad=curiosidad, especies=especies, estados=estados)

# Ruta para eliminar una curiosidad
@app.route('/curiosidades/eliminar/<int:id>')
def eliminar_curiosidad(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM CuriosidadesArbol WHERE IDCuriosidad = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Curiosidad eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar curiosidad: {str(e)}', 'error')
    return redirect(url_for('curiosidades'))

# Ruta para la gestión de interacciones ecológicas
@app.route('/interacciones', methods=['GET', 'POST'])
def interacciones():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Obtener especies para el formulario
        cursor.execute('SELECT * FROM Especie')
        especies = cursor.fetchall()

        if request.method == 'POST':
            try:
                especie = request.form['especie']
                tipo_interaccion = request.form['tipo_interaccion']
                descripcion = request.form['descripcion']
                estado = request.form.get('estado', 1)  # Por defecto activo

                cursor.execute('''
                    INSERT INTO InteraccionesEcologicas (Especie, TipoInteraccion, Descripcion, Estado)
                    VALUES (%s, %s, %s, %s)
                ''', (especie, tipo_interaccion, descripcion, estado))
                connection.commit()
                flash('Interacción ecológica registrada exitosamente', 'success')
                return redirect(url_for('interacciones'))
            except Exception as e:
                flash(f'Error al registrar interacción ecológica: {str(e)}', 'error')

        # Obtener todas las interacciones ecológicas con información de estado
        cursor.execute('''
            SELECT i.*, e.NombreCientifico as EspecieNombre, es.NombreEstado as EstadoNombre
            FROM InteraccionesEcologicas i
            LEFT JOIN Especie e ON i.Especie = e.IDEspecie
            LEFT JOIN Estado es ON i.Estado = es.IDEstado
            ORDER BY i.IDInteraccion DESC
        ''')
        interacciones_list = cursor.fetchall()

        # Obtener estados para el formulario
        cursor.execute('SELECT * FROM Estado')
        estados = cursor.fetchall()

    except Exception as e:
        flash(f'Error al cargar las interacciones ecológicas: {str(e)}', 'error')
        interacciones_list = []
        especies = []
        estados = []
    finally:
        cursor.close()
        connection.close()

    return render_template('interacciones.html', interacciones=interacciones_list, especies=especies, estados=estados)

# Ruta para editar una interacción ecológica
@app.route('/interacciones/editar/<int:id>', methods=['GET', 'POST'])
def editar_interaccion(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        try:
            especie = request.form['especie']
            tipo_interaccion = request.form['tipo_interaccion']
            descripcion = request.form['descripcion']
            estado = request.form.get('estado', 1)  # Por defecto activo

            cursor.execute('''
                UPDATE InteraccionesEcologicas SET Especie = %s, TipoInteraccion = %s, Descripcion = %s, Estado = %s
                WHERE IDInteraccion = %s
            ''', (especie, tipo_interaccion, descripcion, estado, id))
            connection.commit()
            flash('Interacción ecológica actualizada exitosamente', 'success')
            return redirect(url_for('interacciones'))
        except Exception as e:
            flash(f'Error al actualizar interacción ecológica: {str(e)}', 'error')

    # Obtener especies para el formulario
    cursor.execute('SELECT * FROM Especie')
    especies = cursor.fetchall()

    # Obtener la interacción ecológica a editar
    cursor.execute('SELECT * FROM InteraccionesEcologicas WHERE IDInteraccion = %s', (id,))
    interaccion = cursor.fetchone()

    # Obtener estados para el formulario
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()

    if not interaccion:
        flash('Interacción ecológica no encontrada', 'error')
        return redirect(url_for('interacciones'))

    return render_template('editar_interaccion.html', interaccion=interaccion, especies=especies, estados=estados)

# Ruta para eliminar una interacción ecológica
@app.route('/interacciones/eliminar/<int:id>')
def eliminar_interaccion(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM InteraccionesEcologicas WHERE IDInteraccion = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Interacción ecológica eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar interacción ecológica: {str(e)}', 'error')
    return redirect(url_for('interacciones'))

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
            # Iniciar transacción
            connection.begin()

            # Datos básicos del uso
            especie = request.form['especie']
            nombre = request.form['nombre']
            categoria = request.form['categoria']
            estado = request.form.get('estado', 1)  # Por defecto activo

            # Verificar si la columna Categoria existe en la tabla UsoArbol
            cursor.execute('''
                SELECT COUNT(*) AS column_exists
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'UsoArbol'
                  AND COLUMN_NAME = 'Categoria'
            ''')
            column_exists = cursor.fetchone()['column_exists'] > 0

            # Insertar en la tabla UsoArbol
            if column_exists:
                cursor.execute('''
                    INSERT INTO UsoArbol (Especie, Nombre, Categoria, Estado)
                    VALUES (%s, %s, %s, %s)
                ''', (especie, nombre, categoria, estado))
            else:
                cursor.execute('''
                    INSERT INTO UsoArbol (Especie, Nombre, Estado)
                    VALUES (%s, %s, %s)
                ''', (especie, nombre, estado))

            # Obtener el ID del uso recién insertado
            uso_id = cursor.lastrowid

            # Procesar campos específicos según la categoría
            if categoria == 'Maderable':
                dureza = request.form.get('dureza', '')
                resistencia = request.form.get('resistencia', '')
                uso_final = request.form.get('uso_final', '')

                cursor.execute('''
                    INSERT INTO UsoMaderable (Uso, Dureza, Resistencia, UsoFinal, Estado)
                    VALUES (%s, %s, %s, %s, 1)
                ''', (uso_id, dureza, resistencia, uso_final))

            elif categoria == 'Comestible':
                parte_comestible = request.form.get('parte_comestible', '')
                forma_consumo = request.form.get('forma_consumo', '')
                valor_nutricional = request.form.get('valor_nutricional', '')

                cursor.execute('''
                    INSERT INTO UsoComestible (Uso, ParteComestible, FormaConsumo, ValorNutricional, Estado)
                    VALUES (%s, %s, %s, %s, 1)
                ''', (uso_id, parte_comestible, forma_consumo, valor_nutricional))

            elif categoria == 'Medicinal':
                parte_utilizada = request.form.get('parte_utilizada', '')
                preparacion = request.form.get('preparacion', '')
                enfermedades_tratadas = request.form.get('enfermedades_tratadas', '')

                cursor.execute('''
                    INSERT INTO UsoMedicinal (Uso, ParteUtilizada, Preparacion, EnfermedadesTratadas, Estado)
                    VALUES (%s, %s, %s, %s, 1)
                ''', (uso_id, parte_utilizada, preparacion, enfermedades_tratadas))

            elif categoria == 'Ornamental':
                caracteristicas_esteticas = request.form.get('caracteristicas_esteticas', '')
                ubicacion_recomendada = request.form.get('ubicacion_recomendada', '')
                tipo_jardineria = request.form.get('tipo_jardineria', '')
                coloracion_estacional = request.form.get('coloracion_estacional', '')

                cursor.execute('''
                    INSERT INTO UsoOrnamental (Uso, CaracteristicasEsteticas, UbicacionRecomendada, TipoJardineria, ColoracionEstacional, Estado)
                    VALUES (%s, %s, %s, %s, %s, 1)
                ''', (uso_id, caracteristicas_esteticas, ubicacion_recomendada, tipo_jardineria, coloracion_estacional))

            elif categoria == 'Artesanal':
                parte_utilizada = request.form.get('parte_utilizada_artesanal', '')
                tipo_artesania = request.form.get('tipo_artesania', '')
                tecnicas_elaboracion = request.form.get('tecnicas_elaboracion', '')
                comunidades_artesanales = request.form.get('comunidades_artesanales', '')

                cursor.execute('''
                    INSERT INTO UsoArtesanal (Uso, ParteUtilizada, TipoArtesania, TecnicasElaboracion, ComunidadesArtesanales, Estado)
                    VALUES (%s, %s, %s, %s, %s, 1)
                ''', (uso_id, parte_utilizada, tipo_artesania, tecnicas_elaboracion, comunidades_artesanales))

            elif categoria == 'Agroforestal':
                sistema_agroforestal = request.form.get('sistema_agroforestal', '')
                beneficios_asociados = request.form.get('beneficios_asociados', '')
                cultivos_compatibles = request.form.get('cultivos_compatibles', '')
                funcion_principal = request.form.get('funcion_principal', '')

                cursor.execute('''
                    INSERT INTO UsoAgroforestal (Uso, SistemaAgroforestal, BeneficiosAsociados, CultivosCompatibles, FuncionPrincipal, Estado)
                    VALUES (%s, %s, %s, %s, %s, 1)
                ''', (uso_id, sistema_agroforestal, beneficios_asociados, cultivos_compatibles, funcion_principal))

            elif categoria == 'RestauracionEcologica':
                ecosistema_objetivo = request.form.get('ecosistema_objetivo', '')
                funcion_ecologica = request.form.get('funcion_ecologica', '')
                especies_asociadas = request.form.get('especies_asociadas', '')
                tasa_crecimiento = request.form.get('tasa_crecimiento', '')

                cursor.execute('''
                    INSERT INTO UsoRestauracionEcologica (Uso, EcosistemaObjetivo, FuncionEcologica, EspeciesAsociadas, TasaCrecimiento, Estado)
                    VALUES (%s, %s, %s, %s, %s, 1)
                ''', (uso_id, ecosistema_objetivo, funcion_ecologica, especies_asociadas, tasa_crecimiento))

            elif categoria == 'CulturalCeremonial':
                grupo_etnico = request.form.get('grupo_etnico', '')
                tipo_ceremonia = request.form.get('tipo_ceremonia', '')
                significado_cultural = request.form.get('significado_cultural', '')
                parte_utilizada = request.form.get('parte_utilizada_cultural', '')

                cursor.execute('''
                    INSERT INTO UsoCulturalCeremonial (Uso, GrupoEtnico, TipoCeremonia, SignificadoCultural, ParteUtilizada, Estado)
                    VALUES (%s, %s, %s, %s, %s, 1)
                ''', (uso_id, grupo_etnico, tipo_ceremonia, significado_cultural, parte_utilizada))

            elif categoria == 'Melifero':
                tipo_miel = request.form.get('tipo_miel', '')
                epoca_floracion = request.form.get('epoca_floracion', '')
                calidad_polen = request.form.get('calidad_polen', '')
                atraccion_polinizadores = request.form.get('atraccion_polinizadores', '')

                cursor.execute('''
                    INSERT INTO UsoMelifero (Uso, TipoMiel, EpocaFloracion, CalidadPolen, AtraccionPolinizadores, Estado)
                    VALUES (%s, %s, %s, %s, %s, 1)
                ''', (uso_id, tipo_miel, epoca_floracion, calidad_polen, atraccion_polinizadores))

            elif categoria == 'ProteccionAmbiental':
                tipo_proteccion = request.form.get('tipo_proteccion', '')
                beneficios_ambientales = request.form.get('beneficios_ambientales', '')
                zonas_aplicacion = request.form.get('zonas_aplicacion', '')
                capacidad_captura_carbon = request.form.get('capacidad_captura_carbon', '')

                cursor.execute('''
                    INSERT INTO UsoProteccionAmbiental (Uso, TipoProteccion, BeneficiosAmbientales, ZonasAplicacion, CapacidadCapturaCarbon, Estado)
                    VALUES (%s, %s, %s, %s, %s, 1)
                ''', (uso_id, tipo_proteccion, beneficios_ambientales, zonas_aplicacion, capacidad_captura_carbon))

            elif categoria == 'Tintoreo':
                parte_utilizada = request.form.get('parte_utilizada_tintoreo', '')
                color_obtenido = request.form.get('color_obtenido', '')
                metodo_extraccion = request.form.get('metodo_extraccion', '')
                usos_tintes = request.form.get('usos_tintes', '')

                cursor.execute('''
                    INSERT INTO UsoTintoreo (Uso, ParteUtilizada, ColorObtenido, MetodoExtraccion, UsosTintes, Estado)
                    VALUES (%s, %s, %s, %s, %s, 1)
                ''', (uso_id, parte_utilizada, color_obtenido, metodo_extraccion, usos_tintes))

            elif categoria == 'Oleaginoso':
                parte_utilizada = request.form.get('parte_utilizada_oleaginoso', '')
                tipo_aceite = request.form.get('tipo_aceite', '')
                metodo_extraccion = request.form.get('metodo_extraccion_aceite', '')
                propiedades_aceite = request.form.get('propiedades_aceite', '')
                aplicaciones_aceite = request.form.get('aplicaciones_aceite', '')

                cursor.execute('''
                    INSERT INTO UsoOleaginoso (Uso, ParteUtilizada, TipoAceite, MetodoExtraccion, PropiedadesAceite, AplicacionesAceite, Estado)
                    VALUES (%s, %s, %s, %s, %s, %s, 1)
                ''', (uso_id, parte_utilizada, tipo_aceite, metodo_extraccion, propiedades_aceite, aplicaciones_aceite))

            elif categoria == 'Biocombustible':
                tipo_biocombustible = request.form.get('tipo_biocombustible', '')
                poder_calorifico = request.form.get('poder_calorifico', '')
                tasa_crecimiento = request.form.get('tasa_crecimiento_bio', '')
                rendimiento_por_hectarea = request.form.get('rendimiento_por_hectarea', '')

                cursor.execute('''
                    INSERT INTO UsoBiocombustible (Uso, TipoBiocombustible, PoderCalorifico, TasaCrecimiento, RendimientoPorHectarea, Estado)
                    VALUES (%s, %s, %s, %s, %s, 1)
                ''', (uso_id, tipo_biocombustible, poder_calorifico, tasa_crecimiento, rendimiento_por_hectarea))

            # Confirmar transacción
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
        # Obtener especies para el formulario
        cursor.execute('SELECT * FROM Especie')
        especies = cursor.fetchall()

        # Obtener usos de árbol con información de estado
        cursor.execute('''
            SELECT u.*, e.NombreCientifico as EspecieNombre, es.NombreEstado as EstadoNombre,
                   CASE
                       WHEN um.IDUsoMaderable IS NOT NULL THEN 'Maderable'
                       WHEN uc.IDUsoComestible IS NOT NULL THEN 'Comestible'
                       WHEN umed.IDUsoMedicinal IS NOT NULL THEN 'Medicinal'
                       WHEN uo.IDUsoOrnamental IS NOT NULL THEN 'Ornamental'
                       WHEN ua.IDUsoArtesanal IS NOT NULL THEN 'Artesanal'
                       WHEN uaf.IDUsoAgroforestal IS NOT NULL THEN 'Agroforestal'
                       WHEN ure.IDUsoRestauracion IS NOT NULL THEN 'RestauracionEcologica'
                       WHEN ucc.IDUsoCultural IS NOT NULL THEN 'CulturalCeremonial'
                       WHEN umel.IDUsoMelifero IS NOT NULL THEN 'Melifero'
                       WHEN upa.IDUsoProteccion IS NOT NULL THEN 'ProteccionAmbiental'
                       WHEN ut.IDUsoTintoreo IS NOT NULL THEN 'Tintoreo'
                       WHEN uol.IDUsoOleaginoso IS NOT NULL THEN 'Oleaginoso'
                       WHEN ub.IDUsoBiocombustible IS NOT NULL THEN 'Biocombustible'
                       ELSE u.Categoria
                   END AS TipoUsoDetectado
            FROM UsoArbol u
            LEFT JOIN Especie e ON u.Especie = e.IDEspecie
            LEFT JOIN Estado es ON u.Estado = es.IDEstado
            LEFT JOIN UsoMaderable um ON u.IDUso = um.Uso
            LEFT JOIN UsoComestible uc ON u.IDUso = uc.Uso
            LEFT JOIN UsoMedicinal umed ON u.IDUso = umed.Uso
            LEFT JOIN UsoOrnamental uo ON u.IDUso = uo.Uso
            LEFT JOIN UsoArtesanal ua ON u.IDUso = ua.Uso
            LEFT JOIN UsoAgroforestal uaf ON u.IDUso = uaf.Uso
            LEFT JOIN UsoRestauracionEcologica ure ON u.IDUso = ure.Uso
            LEFT JOIN UsoCulturalCeremonial ucc ON u.IDUso = ucc.Uso
            LEFT JOIN UsoMelifero umel ON u.IDUso = umel.Uso
            LEFT JOIN UsoProteccionAmbiental upa ON u.IDUso = upa.Uso
            LEFT JOIN UsoTintoreo ut ON u.IDUso = ut.Uso
            LEFT JOIN UsoOleaginoso uol ON u.IDUso = uol.Uso
            LEFT JOIN UsoBiocombustible ub ON u.IDUso = ub.Uso
            ORDER BY u.IDUso DESC
        ''')
        usos = cursor.fetchall()

        # Obtener estados para el formulario
        cursor.execute('SELECT * FROM Estado')
        estados = cursor.fetchall()

    except Exception as e:
        flash(f'Error al cargar los usos de árbol: {str(e)}', 'error')
        usos = []
        especies = []
        estados = []
    finally:
        cursor.close()
        connection.close()
    return render_template('uso_arbol.html', usos=usos, especies=especies, estados=estados)

# Ruta para editar un uso de árbol
@app.route('/uso_arbol/editar/<int:id>', methods=['GET', 'POST'])
def editar_uso_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        try:
            especie = request.form['especie']
            nombre = request.form['nombre']
            categoria = request.form['categoria']

            connection = get_db_connection()
            cursor = connection.cursor()

            # Verificar si la columna Categoria existe en la tabla UsoArbol
            cursor.execute('''
                SELECT COUNT(*) AS column_exists
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'UsoArbol'
                  AND COLUMN_NAME = 'Categoria'
            ''')
            column_exists = cursor.fetchone()['column_exists'] > 0

            # Actualizar el uso de árbol
            if column_exists:
                cursor.execute('''
                    UPDATE UsoArbol SET Especie = %s, Nombre = %s, Categoria = %s
                    WHERE IDUso = %s
                ''', (especie, nombre, categoria, id))
            else:
                cursor.execute('''
                    UPDATE UsoArbol SET Especie = %s, Nombre = %s
                    WHERE IDUso = %s
                ''', (especie, nombre, id))
            # Procesar campos específicos según la categoría
            if categoria == 'Maderable':
                dureza = request.form.get('dureza', '')
                resistencia = request.form.get('resistencia', '')
                uso_final = request.form.get('uso_final', '')

                # Verificar si ya existe un registro en UsoMaderable
                cursor.execute('SELECT * FROM UsoMaderable WHERE Uso = %s', (id,))
                uso_maderable = cursor.fetchone()

                if uso_maderable:
                    # Actualizar registro existente
                    cursor.execute('''
                        UPDATE UsoMaderable
                        SET Dureza = %s, Resistencia = %s, UsoFinal = %s
                        WHERE Uso = %s
                    ''', (dureza, resistencia, uso_final, id))
                else:
                    # Crear nuevo registro
                    cursor.execute('''
                        INSERT INTO UsoMaderable (Uso, Dureza, Resistencia, UsoFinal, Estado)
                        VALUES (%s, %s, %s, %s, 1)
                    ''', (id, dureza, resistencia, uso_final))

            elif categoria == 'Comestible':
                parte_comestible = request.form.get('parte_comestible', '')
                forma_consumo = request.form.get('forma_consumo', '')
                valor_nutricional = request.form.get('valor_nutricional', '')

                # Verificar si ya existe un registro en UsoComestible
                cursor.execute('SELECT * FROM UsoComestible WHERE Uso = %s', (id,))
                uso_comestible = cursor.fetchone()

                if uso_comestible:
                    # Actualizar registro existente
                    cursor.execute('''
                        UPDATE UsoComestible
                        SET ParteComestible = %s, FormaConsumo = %s, ValorNutricional = %s
                        WHERE Uso = %s
                    ''', (parte_comestible, forma_consumo, valor_nutricional, id))
                else:
                    # Crear nuevo registro
                    cursor.execute('''
                        INSERT INTO UsoComestible (Uso, ParteComestible, FormaConsumo, ValorNutricional, Estado)
                        VALUES (%s, %s, %s, %s, 1)
                    ''', (id, parte_comestible, forma_consumo, valor_nutricional))

            elif categoria == 'Medicinal':
                parte_utilizada = request.form.get('parte_utilizada', '')
                preparacion = request.form.get('preparacion', '')
                enfermedades_tratadas = request.form.get('enfermedades_tratadas', '')

                # Verificar si ya existe un registro en UsoMedicinal
                cursor.execute('SELECT * FROM UsoMedicinal WHERE Uso = %s', (id,))
                uso_medicinal = cursor.fetchone()

                if uso_medicinal:
                    # Actualizar registro existente
                    cursor.execute('''
                        UPDATE UsoMedicinal
                        SET ParteUtilizada = %s, Preparacion = %s, EnfermedadesTratadas = %s
                        WHERE Uso = %s
                    ''', (parte_utilizada, preparacion, enfermedades_tratadas, id))
                else:
                    # Crear nuevo registro
                    cursor.execute('''
                        INSERT INTO UsoMedicinal (Uso, ParteUtilizada, Preparacion, EnfermedadesTratadas, Estado)
                        VALUES (%s, %s, %s, %s, 1)
                    ''', (id, parte_utilizada, preparacion, enfermedades_tratadas))

            elif categoria == 'Ornamental':
                caracteristicas_esteticas = request.form.get('caracteristicas_esteticas', '')
                ubicacion_recomendada = request.form.get('ubicacion_recomendada', '')
                tipo_jardineria = request.form.get('tipo_jardineria', '')
                coloracion_estacional = request.form.get('coloracion_estacional', '')

                # Verificar si ya existe un registro en UsoOrnamental
                cursor.execute('SELECT * FROM UsoOrnamental WHERE Uso = %s', (id,))
                uso_ornamental = cursor.fetchone()

                if uso_ornamental:
                    # Actualizar registro existente
                    cursor.execute('''
                        UPDATE UsoOrnamental
                        SET CaracteristicasEsteticas = %s, UbicacionRecomendada = %s, TipoJardineria = %s, ColoracionEstacional = %s
                        WHERE Uso = %s
                    ''', (caracteristicas_esteticas, ubicacion_recomendada, tipo_jardineria, coloracion_estacional, id))
                else:
                    # Crear nuevo registro
                    cursor.execute('''
                        INSERT INTO UsoOrnamental (Uso, CaracteristicasEsteticas, UbicacionRecomendada, TipoJardineria, ColoracionEstacional, Estado)
                        VALUES (%s, %s, %s, %s, %s, 1)
                    ''', (id, caracteristicas_esteticas, ubicacion_recomendada, tipo_jardineria, coloracion_estacional))

            # Aquí puedes agregar más condiciones para las demás categorías

            connection.commit()
            cursor.close()
            connection.close()
            flash('Uso de árbol actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar el uso de árbol: {str(e)}', 'error')
        return redirect(url_for('uso_arbol'))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener especies para el formulario
    cursor.execute('SELECT * FROM Especie WHERE Estado = 1')
    especies = cursor.fetchall()

    # Obtener el uso de árbol a editar con su categoría detectada
    cursor.execute('''
        SELECT u.*,
               CASE
                   WHEN um.IDUsoMaderable IS NOT NULL THEN 'Maderable'
                   WHEN uc.IDUsoComestible IS NOT NULL THEN 'Comestible'
                   WHEN umed.IDUsoMedicinal IS NOT NULL THEN 'Medicinal'
                   WHEN uo.IDUsoOrnamental IS NOT NULL THEN 'Ornamental'
                   WHEN ua.IDUsoArtesanal IS NOT NULL THEN 'Artesanal'
                   WHEN uaf.IDUsoAgroforestal IS NOT NULL THEN 'Agroforestal'
                   WHEN ure.IDUsoRestauracion IS NOT NULL THEN 'RestauracionEcologica'
                   WHEN ucc.IDUsoCultural IS NOT NULL THEN 'CulturalCeremonial'
                   WHEN umel.IDUsoMelifero IS NOT NULL THEN 'Melifero'
                   WHEN upa.IDUsoProteccion IS NOT NULL THEN 'ProteccionAmbiental'
                   WHEN ut.IDUsoTintoreo IS NOT NULL THEN 'Tintoreo'
                   WHEN uol.IDUsoOleaginoso IS NOT NULL THEN 'Oleaginoso'
                   WHEN ub.IDUsoBiocombustible IS NOT NULL THEN 'Biocombustible'
                   ELSE COALESCE(u.Categoria, 'Otro')
               END AS TipoUsoDetectado
        FROM UsoArbol u
        LEFT JOIN UsoMaderable um ON u.IDUso = um.Uso
        LEFT JOIN UsoComestible uc ON u.IDUso = uc.Uso
        LEFT JOIN UsoMedicinal umed ON u.IDUso = umed.Uso
        LEFT JOIN UsoOrnamental uo ON u.IDUso = uo.Uso
        LEFT JOIN UsoArtesanal ua ON u.IDUso = ua.Uso
        LEFT JOIN UsoAgroforestal uaf ON u.IDUso = uaf.Uso
        LEFT JOIN UsoRestauracionEcologica ure ON u.IDUso = ure.Uso
        LEFT JOIN UsoCulturalCeremonial ucc ON u.IDUso = ucc.Uso
        LEFT JOIN UsoMelifero umel ON u.IDUso = umel.Uso
        LEFT JOIN UsoProteccionAmbiental upa ON u.IDUso = upa.Uso
        LEFT JOIN UsoTintoreo ut ON u.IDUso = ut.Uso
        LEFT JOIN UsoOleaginoso uol ON u.IDUso = uol.Uso
        LEFT JOIN UsoBiocombustible ub ON u.IDUso = ub.Uso
        WHERE u.IDUso = %s
    ''', (id,))
    uso_arbol = cursor.fetchone()

    # Obtener estados
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    # Obtener datos específicos según la categoría
    datos_especificos = {}

    # Maderable
    cursor.execute('SELECT * FROM UsoMaderable WHERE Uso = %s', (id,))
    datos_especificos['maderable'] = cursor.fetchone()

    # Comestible
    cursor.execute('SELECT * FROM UsoComestible WHERE Uso = %s', (id,))
    datos_especificos['comestible'] = cursor.fetchone()

    # Medicinal
    cursor.execute('SELECT * FROM UsoMedicinal WHERE Uso = %s', (id,))
    datos_especificos['medicinal'] = cursor.fetchone()

    # Ornamental
    cursor.execute('SELECT * FROM UsoOrnamental WHERE Uso = %s', (id,))
    datos_especificos['ornamental'] = cursor.fetchone()

    cursor.close()
    connection.close()

    if not uso_arbol:
        flash('Uso de árbol no encontrado', 'error')
        return redirect(url_for('uso_arbol'))

    return render_template('editar_uso_arbol.html', uso_arbol=uso_arbol, especies=especies, estados=estados, datos_especificos=datos_especificos)

# Ruta para editar los detalles de un uso maderable
@app.route('/uso_arbol/maderable/<int:id>', methods=['GET', 'POST'])
def editar_uso_maderable(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Obtener información del uso
        cursor.execute('SELECT * FROM UsoArbol WHERE IDUso = %s', (id,))
        uso = cursor.fetchone()

        if not uso:
            flash('Uso de árbol no encontrado', 'error')
            return redirect(url_for('uso_arbol'))

        # Obtener detalles del uso maderable
        cursor.execute('SELECT * FROM UsoMaderable WHERE Uso = %s', (id,))
        uso_maderable = cursor.fetchone()

        if request.method == 'POST':
            try:
                dureza = request.form['dureza']
                resistencia = request.form['resistencia']
                uso_final = request.form['uso_final']

                if uso_maderable:
                    # Actualizar registro existente
                    cursor.execute('''
                        UPDATE UsoMaderable
                        SET Dureza = %s, Resistencia = %s, UsoFinal = %s
                        WHERE Uso = %s
                    ''', (dureza, resistencia, uso_final, id))
                else:
                    # Crear nuevo registro
                    cursor.execute('''
                        INSERT INTO UsoMaderable (Uso, Dureza, Resistencia, UsoFinal, Estado)
                        VALUES (%s, %s, %s, %s, 1)
                    ''', (id, dureza, resistencia, uso_final))

                connection.commit()
                flash('Detalles de uso maderable actualizados exitosamente', 'success')
                return redirect(url_for('uso_arbol'))
            except Exception as e:
                connection.rollback()
                flash(f'Error al actualizar detalles de uso maderable: {str(e)}', 'error')

        # Si es GET o hubo un error, mostrar el formulario
        return render_template('editar_uso_maderable.html', uso=uso, uso_maderable=uso_maderable)

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('uso_arbol'))
    finally:
        cursor.close()
        connection.close()

# Ruta para editar los detalles de un uso medicinal
@app.route('/uso_arbol/medicinal/<int:id>', methods=['GET', 'POST'])
def editar_uso_medicinal(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Obtener información del uso
        cursor.execute('''
            SELECT u.*, e.NombreCientifico as EspecieNombre
            FROM UsoArbol u
            LEFT JOIN Especie e ON u.Especie = e.IDEspecie
            WHERE u.IDUso = %s
        ''', (id,))
        uso = cursor.fetchone()

        if not uso:
            flash('Uso de árbol no encontrado', 'error')
            return redirect(url_for('uso_arbol'))

        # Obtener detalles del uso maderable
        cursor.execute('SELECT * FROM UsoMaderable WHERE Uso = %s', (id,))
        uso_maderable = cursor.fetchone()

        if request.method == 'POST':
            try:
                dureza = request.form['dureza']
                resistencia = request.form['resistencia']
                uso_final = request.form['uso_final']

                if uso_maderable:
                    # Actualizar registro existente
                    cursor.execute('''
                        UPDATE UsoMaderable
                        SET Dureza = %s, Resistencia = %s, UsoFinal = %s
                        WHERE Uso = %s
                    ''', (dureza, resistencia, uso_final, id))
                else:
                    # Crear nuevo registro
                    cursor.execute('''
                        INSERT INTO UsoMaderable (Uso, Dureza, Resistencia, UsoFinal, Estado)
                        VALUES (%s, %s, %s, %s, 1)
                    ''', (id, dureza, resistencia, uso_final))

                connection.commit()
                flash('Detalles de uso maderable actualizados exitosamente', 'success')
                return redirect(url_for('uso_arbol'))
            except Exception as e:
                connection.rollback()
                flash(f'Error al actualizar detalles de uso maderable: {str(e)}', 'error')

        # Si es GET o hubo un error, mostrar el formulario
        return render_template('editar_uso_maderable.html', uso=uso, uso_maderable=uso_maderable)

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('uso_arbol'))
    finally:
        cursor.close()
        connection.close()

# Ruta para editar los detalles de un uso comestible
@app.route('/uso_arbol/comestible/<int:id>', methods=['GET', 'POST'])
def editar_uso_comestible(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Obtener información del uso
        cursor.execute('''
            SELECT u.*, e.NombreCientifico as EspecieNombre
            FROM UsoArbol u
            LEFT JOIN Especie e ON u.Especie = e.IDEspecie
            WHERE u.IDUso = %s
        ''', (id,))
        uso = cursor.fetchone()

        if not uso:
            flash('Uso de árbol no encontrado', 'error')
            return redirect(url_for('uso_arbol'))

        # Obtener detalles del uso comestible
        cursor.execute('SELECT * FROM UsoComestible WHERE Uso = %s', (id,))
        uso_comestible = cursor.fetchone()

        if request.method == 'POST':
            try:
                parte_comestible = request.form['parte_comestible']
                forma_consumo = request.form['forma_consumo']
                valor_nutricional = request.form['valor_nutricional']

                if uso_comestible:
                    # Actualizar registro existente
                    cursor.execute('''
                        UPDATE UsoComestible
                        SET ParteComestible = %s, FormaConsumo = %s, ValorNutricional = %s
                        WHERE Uso = %s
                    ''', (parte_comestible, forma_consumo, valor_nutricional, id))
                else:
                    # Crear nuevo registro
                    cursor.execute('''
                        INSERT INTO UsoComestible (Uso, ParteComestible, FormaConsumo, ValorNutricional, Estado)
                        VALUES (%s, %s, %s, %s, 1)
                    ''', (id, parte_comestible, forma_consumo, valor_nutricional))

                connection.commit()
                flash('Detalles de uso comestible actualizados exitosamente', 'success')
                return redirect(url_for('uso_arbol'))
            except Exception as e:
                connection.rollback()
                flash(f'Error al actualizar detalles de uso comestible: {str(e)}', 'error')

        # Si es GET o hubo un error, mostrar el formulario
        return render_template('editar_uso_comestible.html', uso=uso, uso_comestible=uso_comestible)

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('uso_arbol'))
    finally:
        cursor.close()
        connection.close()


# Ruta para completar detalles específicos de un uso
@app.route('/uso_arbol/completar/<int:id>/<categoria>', methods=['GET', 'POST'])
def completar_uso_especifico(id, categoria):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    # Redirigir a la ruta específica según la categoría
    if categoria == 'Maderable':
        return redirect(url_for('editar_uso_maderable', id=id))
    elif categoria == 'Comestible':
        return redirect(url_for('editar_uso_comestible', id=id))
    elif categoria == 'Medicinal':
        return redirect(url_for('editar_uso_medicinal', id=id))
    elif categoria == 'Ornamental':
        return redirect(url_for('editar_uso_ornamental', id=id))
    elif categoria == 'Artesanal':
        return redirect(url_for('editar_uso_artesanal', id=id))
    elif categoria == 'Agroforestal':
        return redirect(url_for('editar_uso_agroforestal', id=id))
    elif categoria == 'RestauracionEcologica':
        return redirect(url_for('editar_uso_restauracion', id=id))
    elif categoria == 'CulturalCeremonial':
        return redirect(url_for('editar_uso_cultural', id=id))
    elif categoria == 'Melifero':
        return redirect(url_for('editar_uso_melifero', id=id))
    elif categoria == 'ProteccionAmbiental':
        return redirect(url_for('editar_uso_proteccion', id=id))
    elif categoria == 'Tintoreo':
        return redirect(url_for('editar_uso_tintoreo', id=id))
    elif categoria == 'Oleaginoso':
        return redirect(url_for('editar_uso_oleaginoso', id=id))
    elif categoria == 'Biocombustible':
        return redirect(url_for('editar_uso_biocombustible', id=id))
    else:
        flash(f'No hay un formulario específico para la categoría {categoria}', 'warning')
        return redirect(url_for('uso_arbol'))

# Ruta para editar los detalles de un uso ornamental
@app.route('/uso_arbol/ornamental/<int:id>', methods=['GET', 'POST'])
def editar_uso_ornamental(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Obtener información del uso
        cursor.execute('''
            SELECT u.*, e.NombreCientifico as EspecieNombre
            FROM UsoArbol u
            LEFT JOIN Especie e ON u.Especie = e.IDEspecie
            WHERE u.IDUso = %s
        ''', (id,))
        uso = cursor.fetchone()

        if not uso:
            flash('Uso de árbol no encontrado', 'error')
            return redirect(url_for('uso_arbol'))

        # Obtener detalles del uso ornamental
        cursor.execute('SELECT * FROM UsoOrnamental WHERE Uso = %s', (id,))
        uso_ornamental = cursor.fetchone()

        if request.method == 'POST':
            try:
                caracteristicas_esteticas = request.form['caracteristicas_esteticas']
                ubicacion_recomendada = request.form['ubicacion_recomendada']
                tipo_jardineria = request.form['tipo_jardineria']
                coloracion_estacional = request.form['coloracion_estacional']

                if uso_ornamental:
                    # Actualizar registro existente
                    cursor.execute('''
                        UPDATE UsoOrnamental
                        SET CaracteristicasEsteticas = %s, UbicacionRecomendada = %s, TipoJardineria = %s, ColoracionEstacional = %s
                        WHERE Uso = %s
                    ''', (caracteristicas_esteticas, ubicacion_recomendada, tipo_jardineria, coloracion_estacional, id))
                else:
                    # Crear nuevo registro
                    cursor.execute('''
                        INSERT INTO UsoOrnamental (Uso, CaracteristicasEsteticas, UbicacionRecomendada, TipoJardineria, ColoracionEstacional, Estado)
                        VALUES (%s, %s, %s, %s, %s, 1)
                    ''', (id, caracteristicas_esteticas, ubicacion_recomendada, tipo_jardineria, coloracion_estacional))

                connection.commit()
                flash('Detalles de uso ornamental actualizados exitosamente', 'success')
                return redirect(url_for('uso_arbol'))
            except Exception as e:
                connection.rollback()
                flash(f'Error al actualizar detalles de uso ornamental: {str(e)}', 'error')

        # Si es GET o hubo un error, mostrar el formulario
        return render_template('editar_uso_ornamental.html', uso=uso, uso_ornamental=uso_ornamental)

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('uso_arbol'))
    finally:
        cursor.close()
        connection.close()

# Ruta para mostrar los usos agrupados por especie
@app.route('/usos_por_especie')
def usos_por_especie():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Obtener todas las especies
        cursor.execute('SELECT * FROM Especie ORDER BY NombreCientifico')
        especies = cursor.fetchall()

        # Para cada especie, obtener sus usos
        for especie in especies:
            cursor.execute('''
                SELECT u.*,
                       CASE
                           WHEN um.IDUsoMaderable IS NOT NULL THEN 'Maderable'
                           WHEN uc.IDUsoComestible IS NOT NULL THEN 'Comestible'
                           WHEN umed.IDUsoMedicinal IS NOT NULL THEN 'Medicinal'
                           WHEN uo.IDUsoOrnamental IS NOT NULL THEN 'Ornamental'
                           WHEN ua.IDUsoArtesanal IS NOT NULL THEN 'Artesanal'
                           WHEN uaf.IDUsoAgroforestal IS NOT NULL THEN 'Agroforestal'
                           WHEN ure.IDUsoRestauracion IS NOT NULL THEN 'RestauracionEcologica'
                           WHEN ucc.IDUsoCultural IS NOT NULL THEN 'CulturalCeremonial'
                           WHEN umel.IDUsoMelifero IS NOT NULL THEN 'Melifero'
                           WHEN upa.IDUsoProteccion IS NOT NULL THEN 'ProteccionAmbiental'
                           WHEN ut.IDUsoTintoreo IS NOT NULL THEN 'Tintoreo'
                           WHEN uol.IDUsoOleaginoso IS NOT NULL THEN 'Oleaginoso'
                           WHEN ub.IDUsoBiocombustible IS NOT NULL THEN 'Biocombustible'
                           ELSE u.Categoria
                       END AS TipoUsoDetectado
                FROM UsoArbol u
                LEFT JOIN Especie e ON u.Especie = e.IDEspecie
                LEFT JOIN UsoMaderable um ON u.IDUso = um.Uso
                LEFT JOIN UsoComestible uc ON u.IDUso = uc.Uso
                LEFT JOIN UsoMedicinal umed ON u.IDUso = umed.Uso
                LEFT JOIN UsoOrnamental uo ON u.IDUso = uo.Uso
                LEFT JOIN UsoArtesanal ua ON u.IDUso = ua.Uso
                LEFT JOIN UsoAgroforestal uaf ON u.IDUso = uaf.Uso
                LEFT JOIN UsoRestauracionEcologica ure ON u.IDUso = ure.Uso
                LEFT JOIN UsoCulturalCeremonial ucc ON u.IDUso = ucc.Uso
                LEFT JOIN UsoMelifero umel ON u.IDUso = umel.Uso
                LEFT JOIN UsoProteccionAmbiental upa ON u.IDUso = upa.Uso
                LEFT JOIN UsoTintoreo ut ON u.IDUso = ut.Uso
                LEFT JOIN UsoOleaginoso uol ON u.IDUso = uol.Uso
                LEFT JOIN UsoBiocombustible ub ON u.IDUso = ub.Uso
                WHERE u.Especie = %s
                ORDER BY TipoUsoDetectado, u.Nombre
            ''', (especie['IDEspecie'],))
            especie['usos'] = cursor.fetchall()

        return render_template('usos_por_especie.html', especies=especies)
    except Exception as e:
        flash(f'Error al cargar los usos por especie: {str(e)}', 'error')
        return redirect(url_for('uso_arbol'))
    finally:
        cursor.close()
        connection.close()

# Ruta para agregar un nuevo uso a una especie específica
@app.route('/agregar_uso/<int:especie_id>', methods=['GET', 'POST'])
def agregar_uso(especie_id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Obtener información de la especie
        cursor.execute('SELECT * FROM Especie WHERE IDEspecie = %s', (especie_id,))
        especie = cursor.fetchone()

        if not especie:
            flash('Especie no encontrada', 'error')
            return redirect(url_for('usos_por_especie'))

        if request.method == 'POST':
            # Iniciar transacción
            connection.begin()

            # Datos básicos del uso
            nombre = request.form['nombre']
            categoria = request.form['categoria']

            # Verificar si la columna Categoria existe en la tabla UsoArbol
            cursor.execute('''
                SELECT COUNT(*) AS column_exists
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'UsoArbol'
                  AND COLUMN_NAME = 'Categoria'
            ''')
            column_exists = cursor.fetchone()['column_exists'] > 0

            # Insertar en la tabla UsoArbol
            if column_exists:
                cursor.execute('''
                    INSERT INTO UsoArbol (Especie, Nombre, Categoria, Estado)
                    VALUES (%s, %s, %s, 1)
                ''', (especie_id, nombre, categoria))
            else:
                cursor.execute('''
                    INSERT INTO UsoArbol (Especie, Nombre, Estado)
                    VALUES (%s, %s, 1)
                ''', (especie_id, nombre))

            # Obtener el ID del uso recién insertado
            uso_id = cursor.lastrowid

            # Procesar campos específicos según la categoría
            if categoria == 'Maderable':
                dureza = request.form.get('dureza', '')
                resistencia = request.form.get('resistencia', '')
                uso_final = request.form.get('uso_final', '')

                cursor.execute('''
                    INSERT INTO UsoMaderable (Uso, Dureza, Resistencia, UsoFinal, Estado)
                    VALUES (%s, %s, %s, %s, 1)
                ''', (uso_id, dureza, resistencia, uso_final))

            elif categoria == 'Comestible':
                parte_comestible = request.form.get('parte_comestible', '')
                forma_consumo = request.form.get('forma_consumo', '')
                valor_nutricional = request.form.get('valor_nutricional', '')

                cursor.execute('''
                    INSERT INTO UsoComestible (Uso, ParteComestible, FormaConsumo, ValorNutricional, Estado)
                    VALUES (%s, %s, %s, %s, 1)
                ''', (uso_id, parte_comestible, forma_consumo, valor_nutricional))

            elif categoria == 'Medicinal':
                parte_utilizada = request.form.get('parte_utilizada', '')
                preparacion = request.form.get('preparacion', '')
                enfermedades_tratadas = request.form.get('enfermedades_tratadas', '')

                cursor.execute('''
                    INSERT INTO UsoMedicinal (Uso, ParteUtilizada, Preparacion, EnfermedadesTratadas, Estado)
                    VALUES (%s, %s, %s, %s, 1)
                ''', (uso_id, parte_utilizada, preparacion, enfermedades_tratadas))

            elif categoria == 'Ornamental':
                caracteristicas_esteticas = request.form.get('caracteristicas_esteticas', '')
                ubicacion_recomendada = request.form.get('ubicacion_recomendada', '')
                tipo_jardineria = request.form.get('tipo_jardineria', '')
                coloracion_estacional = request.form.get('coloracion_estacional', '')

                cursor.execute('''
                    INSERT INTO UsoOrnamental (Uso, CaracteristicasEsteticas, UbicacionRecomendada, TipoJardineria, ColoracionEstacional, Estado)
                    VALUES (%s, %s, %s, %s, %s, 1)
                ''', (uso_id, caracteristicas_esteticas, ubicacion_recomendada, tipo_jardineria, coloracion_estacional))

            elif categoria == 'Artesanal':
                parte_utilizada = request.form.get('parte_utilizada_artesanal', '')
                tipo_artesania = request.form.get('tipo_artesania', '')
                tecnicas_elaboracion = request.form.get('tecnicas_elaboracion', '')
                comunidades_artesanales = request.form.get('comunidades_artesanales', '')

                cursor.execute('''
                    INSERT INTO UsoArtesanal (Uso, ParteUtilizada, TipoArtesania, TecnicasElaboracion, ComunidadesArtesanales, Estado)
                    VALUES (%s, %s, %s, %s, %s, 1)
                ''', (uso_id, parte_utilizada, tipo_artesania, tecnicas_elaboracion, comunidades_artesanales))

            # Agregar más condiciones para las demás categorías

            # Confirmar transacción
            connection.commit()
            flash('Uso agregado exitosamente', 'success')
            return redirect(url_for('usos_por_especie'))

        # Si es GET, mostrar el formulario
        return render_template('agregar_uso.html', especie=especie)
    except Exception as e:
        connection.rollback()
        flash(f'Error al agregar uso: {str(e)}', 'error')
        return redirect(url_for('usos_por_especie'))
    finally:
        cursor.close()
        connection.close()

# Ruta para eliminar un uso de árbol
@app.route('/uso_arbol/eliminar/<int:id>')
def eliminar_uso_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Primero, eliminar los registros relacionados en las tablas específicas
        # UsoMaderable
        try:
            cursor.execute('DELETE FROM UsoMaderable WHERE Uso = %s', (id,))
        except Exception as e:
            # Ignorar errores si la tabla no existe o no hay registros
            pass

        # UsoComestible
        try:
            cursor.execute('DELETE FROM UsoComestible WHERE Uso = %s', (id,))
        except Exception as e:
            pass

        # UsoMedicinal
        try:
            cursor.execute('DELETE FROM UsoMedicinal WHERE Uso = %s', (id,))
        except Exception as e:
            pass

        # UsoOrnamental
        try:
            cursor.execute('DELETE FROM UsoOrnamental WHERE Uso = %s', (id,))
        except Exception as e:
            pass

        # UsoArtesanal
        try:
            cursor.execute('DELETE FROM UsoArtesanal WHERE Uso = %s', (id,))
        except Exception as e:
            pass

        # UsoAgroforestal
        try:
            cursor.execute('DELETE FROM UsoAgroforestal WHERE Uso = %s', (id,))
        except Exception as e:
            pass

        # UsoRestauracionEcologica
        try:
            cursor.execute('DELETE FROM UsoRestauracionEcologica WHERE Uso = %s', (id,))
        except Exception as e:
            pass

        # UsoCulturalCeremonial
        try:
            cursor.execute('DELETE FROM UsoCulturalCeremonial WHERE Uso = %s', (id,))
        except Exception as e:
            pass

        # UsoMelifero
        try:
            cursor.execute('DELETE FROM UsoMelifero WHERE Uso = %s', (id,))
        except Exception as e:
            pass

        # UsoProteccionAmbiental
        try:
            cursor.execute('DELETE FROM UsoProteccionAmbiental WHERE Uso = %s', (id,))
        except Exception as e:
            pass

        # UsoTintoreo
        try:
            cursor.execute('DELETE FROM UsoTintoreo WHERE Uso = %s', (id,))
        except Exception as e:
            pass

        # UsoOleaginoso
        try:
            cursor.execute('DELETE FROM UsoOleaginoso WHERE Uso = %s', (id,))
        except Exception as e:
            pass

        # UsoBiocombustible
        try:
            cursor.execute('DELETE FROM UsoBiocombustible WHERE Uso = %s', (id,))
        except Exception as e:
            pass

        # Finalmente, eliminar el registro principal
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
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO tipobosque (Nombre, Descripcion, Estado)
                VALUES (%s, %s, %s)
            ''', (nombre, descripcion, estado))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Tipo de bosque registrado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar el tipo de bosque: {str(e)}', 'error')
        return redirect(url_for('tipo_bosque'))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener tipos de bosque con información de estado
    cursor.execute('''
        SELECT tb.*, e.NombreEstado as EstadoNombre
        FROM TipoBosque tb
        LEFT JOIN Estado e ON tb.Estado = e.IDEstado
        ORDER BY tb.IDTipoBosque DESC
    ''')
    tipos = cursor.fetchall()

    # Obtener estados para el formulario
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('tipo_bosque.html', tipos=tipos, estados=estados)

# Ruta para editar un tipo de bosque
@app.route('/tipo_bosque/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_bosque(id):
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
                UPDATE tipobosque SET Nombre = %s, Descripcion = %s, Estado = %s
                WHERE IDTipoBosque = %s
            ''', (nombre, descripcion, estado, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Tipo de bosque actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar el tipo de bosque: {str(e)}', 'error')
        return redirect(url_for('tipo_bosque'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM tipobosque WHERE IDTipoBosque = %s', (id,))
    tipo_bosque = cursor.fetchone()

    # Obtener estados para el formulario
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('editar_tipo_bosque.html', tipo_bosque=tipo_bosque, estados=estados)

# Ruta para eliminar un tipo de bosque
@app.route('/tipo_bosque/eliminar/<int:id>')
def eliminar_tipo_bosque(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM tipobosque WHERE IDTipoBosque = %s', (id,))
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

        # Ya no es necesario verificar relaciones con MedidasArbol porque la columna ya no existe

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

    # Obtener la lista de árboles para el formulario
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Consulta actualizada para obtener árboles con sus especies
        cursor.execute('''
            SELECT DISTINCT
                a.IDArbol,
                e.NombreCientifico,
                e.NombreVulgar,
                c.NombreCentro
            FROM Arbol a
            JOIN Especie e ON a.Especie = e.IDEspecie
            JOIN Centro c ON a.Centro = c.IDCentro
            WHERE a.Estado = 1
            ORDER BY e.NombreCientifico, a.IDArbol
        ''')
        arboles = cursor.fetchall()
        print(f"Se encontraron {len(arboles)} árboles para mostrar en el formulario")
        for arbol in arboles:
            print(f"ID: {arbol['IDArbol']}, Nombre: {arbol['NombreCientifico']}")
    except Exception as e:
        print(f"Error al obtener la lista de árboles: {str(e)}")
        arboles = []
    finally:
        cursor.close()

    if request.method == 'POST':
        try:
            # Obtener el ID del árbol seleccionado
            arbol_id = request.form.get('arbol_id')
            tamano = int(request.form.get('tamano', 200))

            print(f"Formulario recibido: arbol_id={arbol_id}, tamano={tamano}")
            print(f"Todos los campos del formulario: {request.form}")

            if not arbol_id:
                flash('Por favor seleccione un árbol', 'error')
                return redirect(url_for('qr'))

            # Obtener información del árbol con su especie
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                SELECT
                    a.*,
                    e.NombreCientifico,
                    e.NombreVulgar,
                    c.NombreCentro
                FROM Arbol a
                JOIN Especie e ON a.Especie = e.IDEspecie
                JOIN Centro c ON a.Centro = c.IDCentro
                WHERE a.IDArbol = %s
            ''', (arbol_id,))
            arbol = cursor.fetchone()
            cursor.close()
            connection.close()

            if not arbol:
                flash('Árbol no encontrado', 'error')
                return redirect(url_for('qr'))

            # Generar el código QR
            try:
                # Importar las bibliotecas necesarias
                import qrcode
                from io import BytesIO
                import base64
                # Importar PIL directamente
                from PIL import Image

                # Crear la URL del árbol específico usando la función de detección automática
                base_url = get_base_url()
                arbol_url = f"{base_url}/ver_arbol/{arbol_id}"
                print(f"Generando código QR para URL: {arbol_url}")
                print(f"URL base detectada: {base_url}")
                print(f"Headers de request: Host={request.headers.get('Host')}, X-Forwarded-Host={request.headers.get('X-Forwarded-Host')}, X-Original-Host={request.headers.get('X-Original-Host')}")

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
            except Exception as qr_error:
                print(f"Error during QR code generation: {str(qr_error)}")
                import traceback
                print(traceback.format_exc())
                raise

            # Obtener la fecha actual
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Guardar el QR en la base de datos
            connection = get_db_connection()
            cursor = connection.cursor()
            try:
                # Verificar si ya existe un QR para este árbol
                cursor.execute('SELECT * FROM CodigoQR WHERE Arbol = %s AND Estado = 1', (arbol_id,))
                qr_existente = cursor.fetchone()
                print(f"QR existente: {qr_existente}")
                print(f"Longitud de qr_data: {len(qr_data)} caracteres")

                try:
                    # Verificar si el árbol existe
                    cursor.execute('SELECT IDArbol FROM Arbol WHERE IDArbol = %s', (arbol_id,))
                    arbol_existe = cursor.fetchone()
                    if not arbol_existe:
                        print(f"Error: El árbol con ID {arbol_id} no existe en la base de datos")
                        flash(f'Error: El árbol con ID {arbol_id} no existe en la base de datos', 'error')
                        return redirect(url_for('qr'))

                    # Verificar si la imagen es demasiado grande
                    print(f"Tamaño de la imagen en base64: {len(qr_data)} bytes")

                    if qr_existente:
                        # Actualizar el QR existente
                        print(f"Actualizando QR existente con ID {qr_existente['IDQR']} para el árbol {arbol_id}")
                        cursor.execute('''
                            UPDATE CodigoQR
                            SET Codigo = %s,
                                Imagen = %s,
                                FechaGeneracion = NOW()
                            WHERE IDQR = %s
                        ''', (arbol_url, qr_data, qr_existente['IDQR']))
                        connection.commit()
                        flash('Código QR actualizado exitosamente', 'success')
                    else:
                        # Insertar un nuevo QR
                        cursor.execute('''
                            INSERT INTO CodigoQR
                            (Arbol, Codigo, Imagen, FechaGeneracion, Estado)
                            VALUES (%s, %s, %s, NOW(), 1)
                        ''', (arbol_id, arbol_url, qr_data))
                        connection.commit()
                        flash('Código QR guardado exitosamente', 'success')
                except Exception as db_insert_error:
                    connection.rollback()
                    print(f"Error al guardar el QR en la base de datos: {str(db_insert_error)}")
                    import traceback
                    print(traceback.format_exc())
                    flash(f'Error al guardar el QR: {str(db_insert_error)}', 'error')
                    return redirect(url_for('qr'))

                # Obtener todos los QRs guardados con información de estado
                cursor.execute('''
                    SELECT
                        qr.IDQR,
                        qr.Arbol,
                        qr.Codigo,
                        qr.Imagen,
                        qr.FechaGeneracion,
                        qr.Estado,
                        e.NombreCientifico,
                        e.NombreVulgar,
                        es.NombreEstado as EstadoNombre
                    FROM CodigoQR qr
                    JOIN Arbol a ON qr.Arbol = a.IDArbol
                    JOIN Especie e ON a.Especie = e.IDEspecie
                    LEFT JOIN Estado es ON qr.Estado = es.IDEstado
                    ORDER BY qr.IDQR DESC
                ''')
                qrs_guardados = cursor.fetchall()
                print(f"Se encontraron {len(qrs_guardados)} QRs guardados")

            except Exception as db_error:
                connection.rollback()
                print(f"Error al guardar el QR en la base de datos: {str(db_error)}")
                flash(f'Error al guardar el QR: {str(db_error)}', 'error')
                qrs_guardados = []

            # Obtener la lista de árboles para el formulario
            cursor.execute('SELECT * FROM Arbol')
            arboles = cursor.fetchall()
            cursor.close()
            connection.close()

            return render_template('qr.html',
                                arboles=arboles,
                                qr_data=qr_data,
                                arbol_seleccionado=arbol,
                                fecha_actual=fecha_actual,
                                qrs_guardados=qrs_guardados)

        except Exception as e:
            # Imprimir el error completo para depuración
            import traceback
            print(f"Error al generar QR: {str(e)}")
            print(traceback.format_exc())

            # Mensaje de error más amigable para el usuario
            if "No module named 'PIL'" in str(e):
                flash('Error al generar el QR: Falta la biblioteca PIL. Por favor, instale Pillow con "pip install Pillow".', 'error')
            else:
                flash(f'Error al generar el QR: {str(e)}', 'error')
            return redirect(url_for('qr'))

    # GET request - mostrar el formulario y los QRs guardados
    # Nota: Ya hemos obtenido la lista de árboles al principio de la función
    # Solo necesitamos obtener los QRs guardados

    # Obtener todos los QRs guardados
    try:
        print("Obteniendo QRs guardados...")
        # Crear una nueva conexión para asegurarnos de que estamos obteniendo datos actualizados
        connection_qrs = get_db_connection()
        cursor_qrs = connection_qrs.cursor()

        # Consulta para obtener todos los QRs con información de estado
        cursor_qrs.execute('''
            SELECT
                qr.IDQR,
                qr.Arbol,
                qr.Codigo,
                qr.Imagen,
                qr.FechaGeneracion,
                qr.Estado,
                e.NombreCientifico,
                e.NombreVulgar,
                es.NombreEstado as EstadoNombre
            FROM CodigoQR qr
            JOIN Arbol a ON qr.Arbol = a.IDArbol
            JOIN Especie e ON a.Especie = e.IDEspecie
            LEFT JOIN Estado es ON qr.Estado = es.IDEstado
            WHERE qr.Estado = 1
            ORDER BY qr.IDQR DESC
        ''')
        qrs_guardados = cursor_qrs.fetchall()
        print(f"Se encontraron {len(qrs_guardados)} QRs guardados en la consulta GET")

        # Cerrar la conexión específica para QRs
        cursor_qrs.close()
        connection_qrs.close()

    except Exception as db_error:
        print(f"Error al obtener los QRs guardados: {str(db_error)}")
        import traceback
        print(traceback.format_exc())
        qrs_guardados = []

    # Cerrar la conexión original
    cursor.close()
    connection.close()
    return render_template('qr.html', arboles=arboles, qrs_guardados=qrs_guardados)

# Ruta para ver un QR específico
@app.route('/ver_qr/<int:id>')
def ver_qr(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Obtener el QR y la información del árbol
        cursor.execute('''
            SELECT
                qr.IDQR,
                qr.Arbol,
                qr.Codigo,
                qr.Imagen,
                qr.FechaGeneracion,
                e.NombreCientifico,
                e.NombreVulgar,
                a.Caracteristicas
            FROM CodigoQR qr
            JOIN Arbol a ON qr.Arbol = a.IDArbol
            JOIN Especie e ON a.Especie = e.IDEspecie
            WHERE qr.IDQR = %s
        ''', (id,))
        qr_info = cursor.fetchone()

        cursor.close()
        connection.close()

        if not qr_info:
            flash('Código QR no encontrado', 'error')
            return redirect(url_for('qr'))

        # Obtener la fecha actual
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        return render_template('ver_qr.html', qr_info=qr_info, fecha_actual=fecha_actual)

    except Exception as e:
        flash(f'Error al obtener el QR: {str(e)}', 'error')
        return redirect(url_for('qr'))

# Ruta para eliminar un QR
@app.route('/eliminar_qr/<int:id>', methods=['POST'])
def eliminar_qr(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Verificar si el QR existe
        cursor.execute('SELECT * FROM CodigoQR WHERE IDQR = %s', (id,))
        qr_info = cursor.fetchone()

        if not qr_info:
            flash('Código QR no encontrado', 'error')
            return redirect(url_for('qr'))

        print(f"Eliminando código QR con ID: {id}, asociado al árbol ID: {qr_info['Arbol']}")

        # Marcar el QR como inactivo en lugar de eliminarlo (Estado = 2 es "Inactivo")
        cursor.execute('UPDATE CodigoQR SET Estado = 2 WHERE IDQR = %s', (id,))
        connection.commit()

        print(f"Código QR eliminado exitosamente")

        cursor.close()
        connection.close()

        flash(f'Código QR eliminado exitosamente. Ahora puedes generar un nuevo código QR para el árbol.', 'success')
        return redirect(url_for('qr'))

    except Exception as e:
        print(f"Error al eliminar el QR: {str(e)}")
        import traceback
        print(traceback.format_exc())
        flash(f'Error al eliminar el QR: {str(e)}', 'error')
        return redirect(url_for('qr'))

# Ruta para registrar sugerencias desde la página principal
@app.route('/registrar_sugerencia', methods=['POST'])
def registrar_sugerencia():
    if not session.get('usuario'):
        return jsonify({
            'success': False,
            'message': 'Debes iniciar sesión para enviar sugerencias'
        }), 401

    connection = None
    cursor = None
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
        email = session['usuario']['Correo']

        connection = get_db_connection()
        cursor = connection.cursor()

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

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error al registrar sugerencia: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al guardar en la base de datos: {str(e)}'
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Función para actualizar automáticamente el estado de las sugerencias antiguas
def actualizar_sugerencias_antiguas():
    try:
        # Calcular la fecha límite (1 mes atrás)
        fecha_limite = datetime.now() - timedelta(days=30)
        fecha_limite_str = fecha_limite.strftime('%Y-%m-%d %H:%M:%S')

        connection = get_db_connection()
        cursor = connection.cursor()

        # Actualizar sugerencias más antiguas que 1 mes a estado inactivo (2)
        cursor.execute('''
            UPDATE sugerencias
            SET Estado = 2
            WHERE Estado = 1 AND Fecha < %s
        ''', (fecha_limite_str,))

        num_actualizadas = cursor.rowcount
        connection.commit()
        cursor.close()
        connection.close()

        if num_actualizadas > 0:
            print(f"Se actualizaron {num_actualizadas} sugerencias antiguas a estado inactivo")

        return num_actualizadas
    except Exception as e:
        print(f"Error al actualizar sugerencias antiguas: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return 0

# Ruta para la gestión de sugerencias
@app.route('/sugerencias', methods=['GET', 'POST'])
def sugerencias():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    # Actualizar automáticamente las sugerencias antiguas
    num_actualizadas = actualizar_sugerencias_antiguas()
    if num_actualizadas > 0:
        flash(f'Se actualizaron {num_actualizadas} sugerencias antiguas a estado inactivo', 'info')

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
            SELECT s.*, e.NombreEstado as EstadoNombre
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
        if cursor:
            cursor.close()
        if connection:
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
@app.route('/sugerencias/actualizar/<int:id>', methods=['POST'])
def actualizar_estado_sugerencia(id):
    if 'usuario' not in session:
        return jsonify({
            'success': False,
            'message': 'Debes iniciar sesión para realizar esta acción'
        }), 401

    try:
        nuevo_estado = request.form['estado']
        connection = get_db_connection()
        cursor = connection.cursor()

        # Obtener el nombre de la sugerencia para el mensaje
        cursor.execute('SELECT Nombre FROM sugerencias WHERE IDSugerencia = %s', (id,))
        sugerencia = cursor.fetchone()
        nombre_sugerencia = sugerencia['Nombre'] if sugerencia else 'desconocida'

        # Actualizar el estado
        cursor.execute('''
            UPDATE sugerencias SET Estado = %s
            WHERE IDSugerencia = %s
        ''', (nuevo_estado, id))
        connection.commit()

        # Obtener el nombre del estado
        cursor.execute('SELECT NombreEstado FROM Estado WHERE IDEstado = %s', (nuevo_estado,))
        estado = cursor.fetchone()
        estado_desc = estado['NombreEstado'] if estado else ('Activo' if nuevo_estado == '1' else 'Inactivo')

        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': f'Estado de la sugerencia de {nombre_sugerencia} actualizado a {estado_desc}',
            'nuevoEstado': nuevo_estado,
            'estadoDescripcion': estado_desc
        })
    except Exception as e:
        print(f"Error al actualizar estado de sugerencia: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Error al actualizar el estado: {str(e)}'
        }), 500

# Ruta para la gestión de perfil
@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('iniciar_sesion'))

    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Cargar la información actualizada del usuario desde la base de datos
        cursor.execute('SELECT * FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
        usuario_db = cursor.fetchone()

        if usuario_db:
            # Actualizar la sesión con los datos más recientes
            nombre_completo = usuario_db['Nombre'] if usuario_db['Nombre'] else ''
            partes_nombre = nombre_completo.split(' ', 1)
            nombres = partes_nombre[0] if len(partes_nombre) > 0 else ''
            apellidos = partes_nombre[1] if len(partes_nombre) > 1 else ''

            session['usuario']['Nombre'] = nombre_completo
            session['usuario']['Nombres'] = nombres
            session['usuario']['Apellidos'] = apellidos
            session['usuario']['Correo'] = usuario_db['Correo']
            session['usuario']['Telefono'] = usuario_db['Telefono']
            session['usuario']['Imagen'] = usuario_db['Imagen']

            # Imprimir información de depuración
            print(f"Información de usuario actualizada en sesión: {session['usuario']}")

        if request.method == 'POST':
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            correo = request.form['correo']
            telefono = request.form['telefono']
            nombre_completo = nombres + ' ' + apellidos

            # Verificar si el correo ya existe (excluyendo el usuario actual)
            cursor.execute('''
                SELECT IDUsuario FROM Usuario
                WHERE Correo = %s AND IDUsuario != %s
            ''', (correo, session['usuario']['IDUsuario']))

            if cursor.fetchone():
                flash('El correo electrónico ya está registrado por otro usuario', 'error')
                return redirect(url_for('perfil'))

            # Obtener la imagen actual del usuario
            cursor.execute('SELECT Imagen FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
            usuario_actual = cursor.fetchone()
            imagen_actual = usuario_actual['Imagen'] if usuario_actual else None

            # Procesar la imagen si se ha subido una nueva
            imagen_path = imagen_actual
            if 'avatar' in request.files and request.files['avatar'].filename != '':
                imagen = request.files['avatar']
                # Crear directorio para imágenes si no existe
                upload_folder = os.path.join('static', 'uploads', 'usuarios')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                # Guardar la imagen con un nombre único basado en la fecha y el ID de usuario
                safe_filename = imagen.filename.replace(' ', '_').replace('%', '_').replace('\\', '_').replace('/', '_')
                filename = f"usuario_{session['usuario']['IDUsuario']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_filename}"
                # Usar rutas con barras normales para URLs
                imagen_path = f'uploads/usuarios/{filename}'
                imagen_full_path = os.path.join('static', imagen_path)

                imagen.save(imagen_full_path)

            cursor.execute('''
                UPDATE Usuario
                SET Nombre = %s, Correo = %s, Telefono = %s, Imagen = %s
                WHERE IDUsuario = %s
            ''', (nombre_completo, correo, telefono, imagen_path, session['usuario']['IDUsuario']))
            connection.commit()

            # Actualizar datos en la sesión solo después de la actualización exitosa
            session['usuario']['Nombre'] = nombre_completo
            session['usuario']['Correo'] = correo
            # Mantener nombres y apellidos separados en la sesión para la interfaz
            session['usuario']['Nombres'] = nombres
            session['usuario']['Apellidos'] = apellidos
            session['usuario']['Telefono'] = telefono
            session['usuario']['Imagen'] = imagen_path

            # Forzar la actualización de la sesión
            session.modified = True

            # Imprimir información de depuración
            print(f"Perfil actualizado en sesión: {session['usuario']}")

            flash('Perfil actualizado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al actualizar el perfil: {str(e)}', 'error')
    finally:
        if connection:
            connection.close()

    # Obtener la fecha de registro del usuario
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT DATE_FORMAT(FechaRegistro, "%d/%m/%Y") as FechaRegistro FROM Usuario WHERE IDUsuario = %s',
                       (session['usuario']['IDUsuario'],))
        resultado = cursor.fetchone()
        fecha_registro = resultado['FechaRegistro'] if resultado and 'FechaRegistro' in resultado else 'No disponible'
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error al obtener fecha de registro: {str(e)}")
        fecha_registro = 'No disponible'

    return render_template('perfil.html', fecha_registro=fecha_registro)

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
        cursor.execute('SELECT Contraseña FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
        usuario = cursor.fetchone()

        if usuario['Contraseña'] != contrasena_actual:
            flash('La contraseña actual es incorrecta', 'error')
            cursor.close()
            connection.close()
            return redirect(url_for('perfil'))

        cursor.execute('''
            UPDATE Usuario SET Contraseña = %s
            WHERE IDUsuario = %s
        ''', (nueva_contrasena, session['usuario']['IDUsuario']))
        connection.commit()
        cursor.close()
        connection.close()

        flash('Contraseña actualizada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al cambiar la contraseña: {str(e)}', 'error')
    return redirect(url_for('perfil'))

# Ruta para actualizar el avatar del usuario
@app.route('/actualizar_avatar', methods=['POST'])
def actualizar_avatar():
    if 'usuario' not in session:
        return jsonify({
            'success': False,
            'message': 'Debes iniciar sesión para realizar esta acción'
        }), 401

    try:
        if 'avatar' not in request.files or request.files['avatar'].filename == '':
            return jsonify({
                'success': False,
                'message': 'No se ha seleccionado ninguna imagen'
            }), 400

        # Obtener la imagen actual del usuario
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT Imagen FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
        usuario_actual = cursor.fetchone()
        imagen_actual = usuario_actual['Imagen'] if usuario_actual else None

        # Procesar la nueva imagen
        imagen = request.files['avatar']
        # Crear directorio para imágenes si no existe
        upload_folder = os.path.join('static', 'uploads', 'usuarios')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Guardar la imagen con un nombre único
        safe_filename = imagen.filename.replace(' ', '_').replace('%', '_').replace('\\', '_').replace('/', '_')
        filename = f"usuario_{session['usuario']['IDUsuario']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_filename}"
        imagen_path = f'uploads/usuarios/{filename}'
        imagen_full_path = os.path.join('static', imagen_path)

        imagen.save(imagen_full_path)

        # Actualizar la base de datos
        cursor.execute('UPDATE Usuario SET Imagen = %s WHERE IDUsuario = %s',
                       (imagen_path, session['usuario']['IDUsuario']))
        connection.commit()

        # Actualizar la sesión
        session['usuario']['Imagen'] = imagen_path

        # Forzar la actualización de la sesión
        session.modified = True

        # Imprimir información de depuración
        print(f"Avatar actualizado en sesión: {session['usuario']['Imagen']}")

        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': 'Avatar actualizado exitosamente',
            'imagen_path': url_for('static', filename=imagen_path) if imagen_path else ''
        })
    except Exception as e:
        print(f"Error al actualizar avatar: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Error al actualizar el avatar: {str(e)}'
        }), 500

# Ruta para eliminar el avatar del usuario
@app.route('/eliminar_avatar', methods=['POST'])
def eliminar_avatar():
    if 'usuario' not in session:
        return jsonify({
            'success': False,
            'message': 'Debes iniciar sesión para realizar esta acción'
        }), 401

    try:
        # Determinar el avatar predeterminado basado en el nombre
        nombre = session['usuario']['Nombres']
        avatar_predeterminado = obtener_avatar_predeterminado(nombre)

        # Actualizar la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('UPDATE Usuario SET Imagen = %s WHERE IDUsuario = %s',
                      (avatar_predeterminado, session['usuario']['IDUsuario']))
        connection.commit()

        # Actualizar la sesión
        session['usuario']['Imagen'] = avatar_predeterminado
        session.modified = True

        cursor.close()
        connection.close()

        # Imprimir información de depuración
        print(f"Avatar predeterminado: {avatar_predeterminado}")
        print(f"URL completa: {url_for('static', filename=avatar_predeterminado)}")

        # Asegurarnos de que la imagen exista
        imagen_path = url_for('static', filename=avatar_predeterminado)

        return jsonify({
            'success': True,
            'message': 'Avatar eliminado exitosamente',
            'imagen_path': imagen_path
        })
    except Exception as e:
        print(f"Error al eliminar avatar: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Error al eliminar el avatar: {str(e)}'
        }), 500



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
        cursor.execute('SELECT Contraseña FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
        usuario = cursor.fetchone()

        if usuario['Contraseña'] != contrasena:
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
        # Crear una nueva conexión para esta solicitud
        connection = get_db_connection()
        cursor = connection.cursor()

        # Consulta para obtener todos los datos necesarios del árbol
        # Primero, obtener los campos directamente de la tabla Arbol
        cursor.execute('''
            SELECT * FROM Arbol WHERE IDArbol = %s
        ''', (id,))

        arbol_base = cursor.fetchone()

        if not arbol_base:
            flash('Árbol no encontrado', 'error')
            return redirect(url_for('principal'))

        # Ahora, obtener los datos de las tablas relacionadas
        cursor.execute('''
            SELECT
                e.NombreCientifico as EspecieNombreCientifico,
                e.NombreVulgar as EspecieNombreVulgar,
                tb.Nombre as TipoBosqueNombre,
                tb.Descripcion as TipoBosqueDescripcion,
                c.NombreCentro as CentroNombre,
                est.NombreEstado as EstadoDescripcion
            FROM Especie e, TipoBosque tb, Centro c, Estado est
            WHERE e.IDEspecie = %s
            AND tb.IDTipoBosque = %s
            AND c.IDCentro = %s
            AND est.IDEstado = %s
        ''', (arbol_base['Especie'], arbol_base['TipoBosque'], arbol_base['Centro'], arbol_base['Estado']))

        # Los campos problemáticos están en arbol_base

        # Obtener los datos relacionados
        datos_relacionados = cursor.fetchone()

        # Combinar los datos base del árbol con los datos relacionados
        arbol = {}

        # Primero, copiar todos los campos del árbol base
        for campo, valor in arbol_base.items():
            arbol[campo] = valor

        # Asegurarse de que los campos problemáticos se copien correctamente
        arbol['Descripcion'] = arbol_base.get('Descripcion')
        arbol['Caracteristicas'] = arbol_base.get('Caracteristicas')
        arbol['ServiciosEcosistemicos'] = arbol_base.get('ServiciosEcosistemicos')

        # Luego, agregar los campos de las tablas relacionadas
        if datos_relacionados:
            for campo, valor in datos_relacionados.items():
                arbol[campo] = valor

        # Verificar y establecer valores predeterminados para los campos de texto

        # Forzar valores directamente en el HTML
        descripcion_valor = arbol.get('Descripcion')
        if descripcion_valor is None or descripcion_valor == '':
            descripcion_valor = 'No hay descripción disponible para este árbol.'

        caracteristicas_valor = arbol.get('Caracteristicas')
        if caracteristicas_valor is None or caracteristicas_valor == '':
            caracteristicas_valor = 'No hay características disponibles para este árbol.'

        servicios_valor = arbol.get('ServiciosEcosistemicos')
        if servicios_valor is None or servicios_valor == '':
            servicios_valor = 'No hay servicios ecosistémicos disponibles para este árbol.'

        # Crear HTML directo para estos campos
        arbol['DescripcionHTML'] = f'<div class="text-full"><h6 class="text-center mb-3">Descripción</h6><p>{descripcion_valor}</p></div>'
        arbol['CaracteristicasHTML'] = f'<div class="text-full"><h6 class="text-center mb-3">Características</h6><p>{caracteristicas_valor}</p></div>'
        arbol['ServiciosHTML'] = f'<div class="text-full"><h6 class="text-center mb-3">Servicios Ecosistémicos</h6><p>{servicios_valor}</p></div>'

        # Los valores ya están correctamente establecidos

        # Eliminar la consulta adicional a TipoBosque ya que tenemos los datos necesarios

        # Corregir la ruta de la imagen si existe
        if arbol and arbol['Imagen']:
            # Reemplazar barras invertidas por barras normales
            arbol['Imagen'] = arbol['Imagen'].replace('\\', '/')
            print(f"Imagen del árbol {id}: {arbol['Imagen']}")

        # Obtener el número de árboles en el centro principal
        if arbol and 'Centro' in arbol and arbol['Centro']:
            cursor.execute('SELECT COUNT(*) as total FROM Arbol WHERE Centro = %s', (arbol['Centro'],))
            centro_count = cursor.fetchone()
            arbol['ArbolesEnCentro'] = centro_count['total'] if centro_count else 0
        else:
            arbol['ArbolesEnCentro'] = 0

        # Obtener los usos del árbol
        if arbol and 'Especie' in arbol and arbol['Especie']:
            # Obtener todos los usos para esta especie
            cursor.execute('''
                SELECT
                    ua.IDUso,
                    ua.Categoria,
                    ua.Nombre
                FROM UsoArbol ua
                WHERE ua.Especie = %s AND ua.Estado = 1
            ''', (arbol['Especie'],))
            usos = cursor.fetchall()

            # Inicializar lista para almacenar los usos con sus detalles
            usos_detallados = []

            # Para cada uso, obtener los detalles específicos según su categoría
            for uso in usos:
                uso_detalle = {
                    'IDUso': uso['IDUso'],
                    'Categoria': uso['Categoria'],
                    'Nombre': uso['Nombre'],
                    'Detalles': {}
                }

                # Determinar la tabla específica según la categoría
                if uso['Categoria'] == 'Maderable':
                    cursor.execute('''
                        SELECT * FROM UsoMaderable WHERE Uso = %s AND Estado = 1
                    ''', (uso['IDUso'],))
                    detalle = cursor.fetchone()
                    if detalle:
                        uso_detalle['Detalles'] = detalle

                elif uso['Categoria'] == 'Comestible':
                    cursor.execute('''
                        SELECT * FROM UsoComestible WHERE Uso = %s AND Estado = 1
                    ''', (uso['IDUso'],))
                    detalle = cursor.fetchone()
                    if detalle:
                        uso_detalle['Detalles'] = detalle

                elif uso['Categoria'] == 'Medicinal':
                    cursor.execute('''
                        SELECT * FROM UsoMedicinal WHERE Uso = %s AND Estado = 1
                    ''', (uso['IDUso'],))
                    detalle = cursor.fetchone()
                    if detalle:
                        uso_detalle['Detalles'] = detalle

                elif uso['Categoria'] == 'Ornamental':
                    cursor.execute('''
                        SELECT * FROM UsoOrnamental WHERE Uso = %s AND Estado = 1
                    ''', (uso['IDUso'],))
                    detalle = cursor.fetchone()
                    if detalle:
                        uso_detalle['Detalles'] = detalle

                elif uso['Categoria'] == 'Artesanal':
                    cursor.execute('''
                        SELECT * FROM UsoArtesanal WHERE Uso = %s AND Estado = 1
                    ''', (uso['IDUso'],))
                    detalle = cursor.fetchone()
                    if detalle:
                        uso_detalle['Detalles'] = detalle

                elif uso['Categoria'] == 'Agroforestal':
                    cursor.execute('''
                        SELECT * FROM UsoAgroforestal WHERE Uso = %s AND Estado = 1
                    ''', (uso['IDUso'],))
                    detalle = cursor.fetchone()
                    if detalle:
                        uso_detalle['Detalles'] = detalle

                elif uso['Categoria'] == 'RestauracionEcologica':
                    cursor.execute('''
                        SELECT * FROM UsoRestauracionEcologica WHERE Uso = %s AND Estado = 1
                    ''', (uso['IDUso'],))
                    detalle = cursor.fetchone()
                    if detalle:
                        uso_detalle['Detalles'] = detalle

                elif uso['Categoria'] == 'CulturalCeremonial':
                    cursor.execute('''
                        SELECT * FROM UsoCulturalCeremonial WHERE Uso = %s AND Estado = 1
                    ''', (uso['IDUso'],))
                    detalle = cursor.fetchone()
                    if detalle:
                        uso_detalle['Detalles'] = detalle

                elif uso['Categoria'] == 'Melifero':
                    cursor.execute('''
                        SELECT * FROM UsoMelifero WHERE Uso = %s AND Estado = 1
                    ''', (uso['IDUso'],))
                    detalle = cursor.fetchone()
                    if detalle:
                        uso_detalle['Detalles'] = detalle

                elif uso['Categoria'] == 'ProteccionAmbiental':
                    cursor.execute('''
                        SELECT * FROM UsoProteccionAmbiental WHERE Uso = %s AND Estado = 1
                    ''', (uso['IDUso'],))
                    detalle = cursor.fetchone()
                    if detalle:
                        uso_detalle['Detalles'] = detalle

                elif uso['Categoria'] == 'Tintoreo':
                    cursor.execute('''
                        SELECT * FROM UsoTintoreo WHERE Uso = %s AND Estado = 1
                    ''', (uso['IDUso'],))
                    detalle = cursor.fetchone()
                    if detalle:
                        uso_detalle['Detalles'] = detalle

                elif uso['Categoria'] == 'Oleaginoso':
                    cursor.execute('''
                        SELECT * FROM UsoOleaginoso WHERE Uso = %s AND Estado = 1
                    ''', (uso['IDUso'],))
                    detalle = cursor.fetchone()
                    if detalle:
                        uso_detalle['Detalles'] = detalle

                elif uso['Categoria'] == 'Biocombustible':
                    cursor.execute('''
                        SELECT * FROM UsoBiocombustible WHERE Uso = %s AND Estado = 1
                    ''', (uso['IDUso'],))
                    detalle = cursor.fetchone()
                    if detalle:
                        uso_detalle['Detalles'] = detalle

                # Agregar el uso con sus detalles a la lista
                usos_detallados.append(uso_detalle)

            # Asignar la lista de usos al árbol
            arbol['Usos'] = usos_detallados
        else:
            arbol['Usos'] = []

        # Obtener las curiosidades del árbol
        if arbol and 'Especie' in arbol and arbol['Especie']:
            cursor.execute('''
                SELECT * FROM CuriosidadesArbol
                WHERE Especie = %s AND Estado = 1
            ''', (arbol['Especie'],))
            curiosidades = cursor.fetchall()
            arbol['Curiosidades'] = curiosidades
        else:
            arbol['Curiosidades'] = []

        # Obtener las interacciones ecológicas del árbol
        if arbol and 'Especie' in arbol and arbol['Especie']:
            cursor.execute('''
                SELECT * FROM InteraccionesEcologicas
                WHERE Especie = %s AND Estado = 1
            ''', (arbol['Especie'],))
            interacciones = cursor.fetchall()
            arbol['Interacciones'] = interacciones
        else:
            arbol['Interacciones'] = []

        # Definir las coordenadas predeterminadas para los centros (solo se usarán si no hay datos en la BD)
        centros_coordenadas = {
            1: {  # Coordenadas predeterminadas para CIGEC (ID 1)
                'nombre': '',  # Se usará el nombre de la base de datos
                'lat': 10.4631,  # Latitud predeterminada para CIGEC
                'lng': -73.2532,  # Longitud predeterminada para CIGEC
                'direccion': ''  # Se usará la dirección de la base de datos
            },
            2: {  # Coordenadas predeterminadas para CBC (ID 2)
                'nombre': '',  # Se usará el nombre de la base de datos
                'lat': 10.4795,  # Latitud predeterminada para CBC
                'lng': -73.2396,  # Longitud predeterminada para CBC
                'direccion': ''  # Se usará la dirección de la base de datos
            }
        }

        # Obtener el centro del árbol y sus coordenadas
        centro_id = arbol.get('Centro') if 'Centro' in arbol else None

        # Obtener información actualizada del centro desde la base de datos
        cursor.execute('SELECT * FROM Centro WHERE IDCentro = %s', (centro_id,))
        centro_db = cursor.fetchone()

        if centro_db:
            # Definir coordenadas precisas para los centros conocidos
            # Estas coordenadas son más precisas que las anteriores
            coordenadas_precisas = {
                1: {  # CIGEC (Centro de Innovación de Gestión Empresarial y Cultural)
                    'lat': 10.4634,
                    'lng': -73.2532,
                    'direccion_precisa': 'Cl. 39 #5-130, Valledupar, Cesar, Colombia'
                },
                2: {  # CBC (Centro Biotecnológico del Caribe)
                    'lat': 10.4795,
                    'lng': -73.2396,
                    'direccion_precisa': 'Km 7 Vía a La Paz, Valledupar, Cesar, Colombia'
                }
            }

            # Usar coordenadas precisas si están disponibles, o las predeterminadas como respaldo
            coordenadas = coordenadas_precisas.get(centro_id, centros_coordenadas.get(centro_id, {
                'lat': 10.4634,  # Coordenadas por defecto
                'lng': -73.2532
            }))

            # Usar siempre la dirección de la base de datos
            direccion = centro_db['Direccion'] if centro_db['Direccion'] else 'Dirección no disponible'

            # Generar siglas del centro
            siglas_centro = ''.join([c[0] for c in centro_db['NombreCentro'].split() if c[0].isupper()])

            arbol['CentroInfo'] = {
                'nombre': centro_db['NombreCentro'],  # Usar siempre el nombre de la base de datos
                'siglas': siglas_centro,  # Agregar siglas
                'lat': coordenadas['lat'],  # Usar coordenadas precisas
                'lng': coordenadas['lng'],
                'direccion': direccion
            }

            # Imprimir información para depuración
            print(f"Centro desde BD: {centro_db['NombreCentro']}")
            print(f"Dirección usada: {direccion}")
            print(f"Coordenadas: {coordenadas['lat']}, {coordenadas['lng']}")
        else:
            # Centro por defecto si no se encuentra
            arbol['CentroInfo'] = {
                'nombre': 'Desconocido',
                'lat': 2.4448,
                'lng': -76.6147,
                'direccion': 'Ubicación no disponible'
            }

        # Obtener el número de árboles en cada centro
        # Obtener todos los centros
        cursor.execute('SELECT IDCentro, NombreCentro FROM Centro')
        centros = cursor.fetchall()

        # Inicializar un diccionario para almacenar los conteos
        arbol['CentrosArboles'] = {}

        # Para cada centro, contar los árboles
        for centro in centros:
            centro_id = centro['IDCentro']
            centro_nombre = centro['NombreCentro']

            cursor.execute('SELECT COUNT(*) as total FROM Arbol WHERE Centro = %s', (centro_id,))
            count = cursor.fetchone()
            total = count['total'] if count else 0

            # Guardar el conteo en el diccionario
            arbol['CentrosArboles'][centro_id] = {
                'nombre': centro_nombre,
                'total': total,
                'siglas': ''.join([c[0] for c in centro_nombre.split() if c[0].isupper()])
            }

            # Mantener compatibilidad con el código existente
            if centro_id == 2:  # CBC (ID 2)
                arbol['ArbolesEnCBC'] = total
            elif centro_id == 1:  # CIGEC (ID 1)
                arbol['ArbolesEnCIGEC'] = total

        # Obtener el código QR asociado al árbol si existe
        try:
            cursor.execute('SELECT * FROM CodigoQR WHERE Arbol = %s AND Estado = 1', (id,))
            qr_info = cursor.fetchone()
            if qr_info:
                print(f"QR encontrado para el árbol {id}: {qr_info['IDQR']}")
                arbol['QR'] = qr_info['Imagen']
            else:
                print(f"No se encontró QR activo para el árbol {id}")
                arbol['QR'] = None
        except Exception as qr_error:
            print(f"Error al buscar QR para el árbol {id}: {str(qr_error)}")
            arbol['QR'] = None

        # Obtener las medidas del árbol (si la tabla existe)
        medidas = []
        try:
            # Verificar si la tabla MedidasArbol existe
            cursor.execute("SHOW TABLES LIKE 'MedidasArbol'")
            if cursor.fetchone():
                cursor.execute('''
                    SELECT *
                    FROM MedidasArbol
                    WHERE Arbol = %s
                    ORDER BY IDMedida DESC
                ''', (id,))
                medidas = cursor.fetchall()
                print(f"Se encontraron {len(medidas)} medidas para el árbol {id}")
            else:
                print(f"La tabla MedidasArbol no existe en la base de datos")
        except Exception as medidas_error:
            print(f"Error al buscar medidas para el árbol {id}: {str(medidas_error)}")

        # La información del centro ya se ha obtenido anteriormente
        # No es necesario volver a obtenerla aquí

        # Los campos de texto ya se han establecido anteriormente

        cursor.close()
        connection.close()

        # Ya verificamos si el árbol existe anteriormente

        # Imprimir los valores finales para depuración
        print("\n==== VALORES FINALES ANTES DE RENDERIZAR ====\n")
        print(f"Descripcion: {arbol.get('Descripcion', 'NO EXISTE')}")
        print(f"Caracteristicas: {arbol.get('Caracteristicas', 'NO EXISTE')}")
        print(f"ServiciosEcosistemicos: {arbol.get('ServiciosEcosistemicos', 'NO EXISTE')}")

        # Verificar una última vez que los campos tengan valores válidos
        if arbol.get('Descripcion') is None or arbol.get('Descripcion') == '':
            arbol['Descripcion'] = 'No hay descripción disponible para este árbol.'
            print("Forzando valor predeterminado para Descripcion en la verificación final")

        if arbol.get('Caracteristicas') is None or arbol.get('Caracteristicas') == '':
            arbol['Caracteristicas'] = 'No hay características disponibles para este árbol.'
            print("Forzando valor predeterminado para Caracteristicas en la verificación final")

        if arbol.get('ServiciosEcosistemicos') is None or arbol.get('ServiciosEcosistemicos') == '':
            arbol['ServiciosEcosistemicos'] = 'No hay servicios ecosistémicos disponibles para este árbol.'
            print("Forzando valor predeterminado para ServiciosEcosistemicos en la verificación final")

        return render_template('ver_arbol.html', arbol=arbol, medidas=medidas)
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
                WHERE Correo = %s AND IDUsuario != %s
            """, (correo, id))
            if cursor.fetchone():
                flash('El correo electrónico ya está registrado', 'error')
                return redirect(url_for('editar_usuario', id=id))

            # Actualizar datos del usuario
            cursor.execute("""
                UPDATE Usuario
                SET Nombre = %s, Correo = %s, Telefono = %s
                WHERE IDUsuario = %s
            """, (nombres + ' ' + apellidos, correo, telefono, id))

            # Actualizar rol del usuario
            cursor.execute("SELECT IDRol FROM Rol WHERE NombreRol = %s", (rol,))
            resultado = cursor.fetchone()
            if resultado:
                id_rol = resultado['IDRol']

                # Verificar si ya existe un rol para este usuario
                cursor.execute("SELECT COUNT(*) as count FROM UsuarioRol WHERE Usuario = %s", (id,))
                existe_rol = cursor.fetchone()['count'] > 0

                if existe_rol:
                    # Actualizar el rol existente
                    cursor.execute("UPDATE UsuarioRol SET Rol = %s WHERE Usuario = %s", (id_rol, id))
                else:
                    # Insertar nuevo rol
                    cursor.execute("INSERT INTO UsuarioRol (Usuario, Rol) VALUES (%s, %s)", (id, id_rol))

            get_db().commit()
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('gestion_usuarios'))

        except Exception as e:
            get_db().rollback()
            flash(f'Error al actualizar usuario: {str(e)}', 'error')
            return redirect(url_for('editar_usuario', id=id))

    # Obtener datos del usuario
    cursor.execute("""
        SELECT u.*, r.NombreRol as rol_actual
        FROM Usuario u
        LEFT JOIN UsuarioRol ur ON u.IDUsuario = ur.Usuario
        LEFT JOIN Rol r ON ur.Rol = r.IDRol
        WHERE u.IDUsuario = %s
    """, (id,))
    usuario = cursor.fetchone()

    # Dividir el nombre completo en nombres y apellidos para la interfaz
    if usuario:
        nombre_completo = usuario['Nombre'] if usuario['Nombre'] else ''
        partes_nombre = nombre_completo.split(' ', 1)
        usuario['Nombres'] = partes_nombre[0] if len(partes_nombre) > 0 else ''
        usuario['Apellidos'] = partes_nombre[1] if len(partes_nombre) > 1 else ''

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
        SELECT r.NombreRol
        FROM UsuarioRol ur
        JOIN Rol r ON ur.Rol = r.IDRol
        WHERE ur.Usuario = %s AND r.NombreRol = 'Administrador'
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



# Rutas para las páginas de información
@app.route('/politica-privacidad')
def politica_privacidad():
    return render_template('politica_privacidad.html')

@app.route('/terminos-condiciones')
def terminos_condiciones():
    return render_template('terminos_condiciones.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/acerca-de')
def acerca_de():
    return render_template('acerca_de.html')

@app.route('/soporte-tecnico')
def soporte_tecnico():
    return render_template('soporte_tecnico.html')

@app.route('/preguntas-frecuentes')
def preguntas_frecuentes():
    return render_template('preguntas_frecuentes.html')

@app.route('/reportar-problema')
def reportar_problema():
    return render_template('reportar_problema.html')

@app.route('/enviar-contacto', methods=['POST'])
def enviar_contacto():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            email = request.form['email']
            telefono = request.form.get('telefono', '')
            asunto = request.form['asunto']
            mensaje = request.form['mensaje']

            # Aquí se podría implementar el envío de correo electrónico
            # o guardar el mensaje en la base de datos

            flash('Mensaje enviado correctamente. Nos pondremos en contacto contigo pronto.', 'success')
        except Exception as e:
            flash(f'Error al enviar el mensaje: {str(e)}', 'error')

        return redirect(url_for('contacto'))

# Ruta para sugerencias de búsqueda (autocompletado)
@app.route('/api/sugerencias_busqueda')
def sugerencias_busqueda():
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify([])

    connection = get_db_connection()
    cursor = connection.cursor()
    sugerencias = []

    try:
        # Buscar especies que coincidan con la consulta
        cursor.execute('''
            SELECT NombreCientifico, NombreVulgar FROM Especie
            WHERE NombreCientifico LIKE %s OR NombreVulgar LIKE %s
            LIMIT 5
        ''', (f'%{query}%', f'%{query}%'))
        especies = cursor.fetchall()

        # Agregar nombres científicos y vulgares a las sugerencias
        for especie in especies:
            if especie['NombreCientifico'] and query.lower() in especie['NombreCientifico'].lower():
                sugerencias.append(especie['NombreCientifico'])
            if especie['NombreVulgar'] and query.lower() in especie['NombreVulgar'].lower():
                sugerencias.append(especie['NombreVulgar'])

        # Buscar centros que coincidan con la consulta
        cursor.execute('''
            SELECT NombreCentro FROM Centro
            WHERE NombreCentro LIKE %s
            LIMIT 3
        ''', (f'%{query}%',))
        centros = cursor.fetchall()

        # Agregar nombres de centros a las sugerencias
        for centro in centros:
            if centro['NombreCentro'] and query.lower() in centro['NombreCentro'].lower():
                sugerencias.append(centro['NombreCentro'])

        # Eliminar duplicados y limitar a 8 sugerencias
        sugerencias = list(set(sugerencias))[:8]

    except Exception as e:
        print(f"Error al obtener sugerencias: {str(e)}")
    finally:
        cursor.close()
        connection.close()

    return jsonify(sugerencias)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)