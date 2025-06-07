import pymysql
from datetime import datetime, timedelta

# Conexión a la base de datos
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='verdeqr',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    cursor = conn.cursor()
    
    # Buscar el usuario por correo
    cursor.execute('SELECT IDUsuario FROM Usuario WHERE Correo = %s', ('jhon123@gmail.com',))
    usuario = cursor.fetchone()
    
    if usuario:
        # Crear un token
        token = '123456'
        fecha_expiracion = datetime.now() + timedelta(minutes=30)
        
        # Guardar el token en la base de datos
        cursor.execute('''
            INSERT INTO tokens_recuperacion (Usuario, Token, FechaExpiracion, Estado)
            VALUES (%s, %s, %s, 1)
        ''', (usuario['IDUsuario'], token, fecha_expiracion))
        
        conn.commit()
        print(f'Token creado: {token}')
    else:
        print('Usuario no encontrado')
        
except Exception as e:
    print(f'Error: {str(e)}')
    conn.rollback()
    
finally:
    conn.close()
