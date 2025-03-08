from flask import Flask
from database import mysql, app  # Importar la configuración de la base de datos

# Importar las rutas
from routes import *

if __name__ == '__main__':
    app.run(debug=True)