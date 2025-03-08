from flask import Flask, render_template, request, redirect, url_for
from database import mysql, app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/arbol', methods=['GET', 'POST'])
def arbol():
    if request.method == 'POST':
        # Procesar el formulario de árbol
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

        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO Arbol (NombreCientifico, NombreVulgar, UbicacionGeografica, Caracteristicas, ServicioEcosistemico, Cantidad, TipoArbol, UsoArbol, TipoBosque, Centro, Estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (nombre_cientifico, nombre_vulgar, ubicacion_geografica, caracteristicas, servicio_ecosistemico, cantidad, tipo_arbol, uso_arbol, tipo_bosque, centro, estado))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('arbol'))

    # Obtener datos para el formulario
    cursor = mysql.connection.cursor()

    # Obtener tipos de árbol
    cursor.execute('SELECT * FROM TipoArbol')
    tipos_arbol = cursor.fetchall()

    # Obtener usos de árbol
    cursor.execute('SELECT * FROM UsoArbol')
    usos_arbol = cursor.fetchall()

    # Obtener tipos de bosque
    cursor.execute('SELECT * FROM TipoBosque')
    tipos_bosque = cursor.fetchall()

    # Obtener centros
    cursor.execute('SELECT * FROM Centro')
    centros = cursor.fetchall()

    # Obtener estados
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()

    return render_template('arbol.html', tipos_arbol=tipos_arbol, usos_arbol=usos_arbol, tipos_bosque=tipos_bosque, centros=centros, estados=estados)

@app.route('/centro', methods=['GET', 'POST'])
def centro():
    if request.method == 'POST':
        # Crear un nuevo centro
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']

        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO Centro (Nombre, Descripcion)
            VALUES (%s, %s)
        ''', (nombre, descripcion))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('centro'))

    # Obtener todos los centros
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Centro')
    centros = cursor.fetchall()
    cursor.close()

    return render_template('centro.html', centros=centros)

@app.route('/centro/editar/<int:id>', methods=['GET', 'POST'])
def editar_centro(id):
    if request.method == 'POST':
        # Actualizar un centro existente
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']

        cursor = mysql.connection.cursor()
        cursor.execute('''
            UPDATE Centro
            SET Nombre = %s, Descripcion = %s
            WHERE IDCentro = %s
        ''', (nombre, descripcion, id))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('centro'))

    # Obtener el centro a editar
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Centro WHERE IDCentro = %s', (id,))
    centro = cursor.fetchone()
    cursor.close()

    return render_template('editar_centro.html', centro=centro)

@app.route('/centro/eliminar/<int:id>')
def eliminar_centro(id):
    # Eliminar un centro
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM Centro WHERE IDCentro = %s', (id,))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('centro'))

@app.route('/tipo_arbol', methods=['GET', 'POST'])
def tipo_arbol():
    if request.method == 'POST':
        # Crear un nuevo tipo de árbol
        nombre_cientifico = request.form['nombre_cientifico']
        nombre_vulgar = request.form['nombre_vulgar']

        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO TipoArbol (NombreCientifico, NombreVulgar)
            VALUES (%s, %s)
        ''', (nombre_cientifico, nombre_vulgar))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('tipo_arbol'))

    # Obtener todos los tipos de árbol
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM TipoArbol')
    tipos_arbol = cursor.fetchall()
    cursor.close()

    return render_template('tipo_arbol.html', tipos_arbol=tipos_arbol)

@app.route('/tipo_arbol/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_arbol(id):
    if request.method == 'POST':
        # Actualizar un tipo de árbol existente
        nombre_cientifico = request.form['nombre_cientifico']
        nombre_vulgar = request.form['nombre_vulgar']

        cursor = mysql.connection.cursor()
        cursor.execute('''
            UPDATE TipoArbol
            SET NombreCientifico = %s, NombreVulgar = %s
            WHERE IDTipoArbol = %s
        ''', (nombre_cientifico, nombre_vulgar, id))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('tipo_arbol'))

    # Obtener el tipo de árbol a editar
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM TipoArbol WHERE IDTipoArbol = %s', (id,))
    tipo_arbol = cursor.fetchone()
    cursor.close()

    return render_template('editar_tipo_arbol.html', tipo_arbol=tipo_arbol)

@app.route('/tipo_arbol/eliminar/<int:id>')
def eliminar_tipo_arbol(id):
    # Eliminar un tipo de árbol
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM TipoArbol WHERE IDTipoArbol = %s', (id,))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('tipo_arbol'))

@app.route('/uso_arbol', methods=['GET', 'POST'])
def uso_arbol():
    if request.method == 'POST':
        # Crear un nuevo uso de árbol
        descripcion = request.form['descripcion']

        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO UsoArbol (Descripcion)
            VALUES (%s)
        ''', (descripcion,))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('uso_arbol'))

    # Obtener todos los usos de árbol
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM UsoArbol')
    usos_arbol = cursor.fetchall()
    cursor.close()

    return render_template('uso_arbol.html', usos_arbol=usos_arbol)

@app.route('/uso_arbol/editar/<int:id>', methods=['GET', 'POST'])
def editar_uso_arbol(id):
    if request.method == 'POST':
        # Actualizar un uso de árbol existente
        descripcion = request.form['descripcion']

        cursor = mysql.connection.cursor()
        cursor.execute('''
            UPDATE UsoArbol
            SET Descripcion = %s
            WHERE IDUso = %s
        ''', (descripcion, id))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('uso_arbol'))

    # Obtener el uso de árbol a editar
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM UsoArbol WHERE IDUso = %s', (id,))
    uso_arbol = cursor.fetchone()
    cursor.close()

    return render_template('editar_uso_arbol.html', uso_arbol=uso_arbol)

@app.route('/uso_arbol/eliminar/<int:id>')
def eliminar_uso_arbol(id):
    # Eliminar un uso de árbol
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM UsoArbol WHERE IDUso = %s', (id,))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('uso_arbol'))