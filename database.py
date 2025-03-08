from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'  # Host de la base de datos
app.config['MYSQL_USER'] = 'root'       # Usuario de MySQL
app.config['MYSQL_PASSWORD'] = ''       # Contraseña de MySQL (deja vacío si no tienes)
app.config['MYSQL_DB'] = 'VerdeQR_Optimizada'  # Nombre de la base de datos
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Usar diccionarios en lugar de tuplas

mysql = MySQL(app)