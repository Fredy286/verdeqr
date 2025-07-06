#!/usr/bin/env python3
"""
Script para migrar la base de datos local a Railway
Ejecutar después de configurar las variables de entorno en Railway
"""

import pymysql
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos local (XAMPP)
LOCAL_DB = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Tu password de XAMPP
    'database': 'VerdeQR',
    'cursorclass': pymysql.cursors.DictCursor
}

# Configuración de base de datos Railway (usar las variables de entorno)
RAILWAY_DB = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME'),
    'cursorclass': pymysql.cursors.DictCursor
}

def test_connections():
    """Probar conexiones a ambas bases de datos"""
    print("🔍 Probando conexiones...")
    
    try:
        local_conn = pymysql.connect(**LOCAL_DB)
        print("✅ Conexión local exitosa")
        local_conn.close()
    except Exception as e:
        print(f"❌ Error conexión local: {e}")
        return False
    
    try:
        railway_conn = pymysql.connect(**RAILWAY_DB)
        print("✅ Conexión Railway exitosa")
        railway_conn.close()
    except Exception as e:
        print(f"❌ Error conexión Railway: {e}")
        return False
    
    return True

def get_table_structure():
    """Obtener estructura de tablas de la base local"""
    conn = pymysql.connect(**LOCAL_DB)
    cursor = conn.cursor()
    
    # Obtener lista de tablas
    cursor.execute("SHOW TABLES")
    tables = [row[f'Tables_in_{LOCAL_DB["database"]}'] for row in cursor.fetchall()]
    
    structure = {}
    for table in tables:
        cursor.execute(f"SHOW CREATE TABLE {table}")
        create_statement = cursor.fetchone()[f'Create Table']
        structure[table] = create_statement
    
    conn.close()
    return structure

def create_tables_in_railway():
    """Crear tablas en Railway"""
    print("🏗️ Creando estructura de tablas en Railway...")
    
    structure = get_table_structure()
    conn = pymysql.connect(**RAILWAY_DB)
    cursor = conn.cursor()
    
    for table_name, create_statement in structure.items():
        try:
            cursor.execute(create_statement)
            print(f"✅ Tabla {table_name} creada")
        except Exception as e:
            print(f"❌ Error creando {table_name}: {e}")
    
    conn.commit()
    conn.close()

def migrate_data():
    """Migrar datos de local a Railway"""
    print("📦 Migrando datos...")
    
    # Orden de tablas para respetar foreign keys
    tables_order = [
        'Rol', 'TipoBosque', 'Centro', 'Especie', 
        'Usuario', 'UsuarioRol', 'Arbol', 'Interaccion'
    ]
    
    local_conn = pymysql.connect(**LOCAL_DB)
    railway_conn = pymysql.connect(**RAILWAY_DB)
    
    local_cursor = local_conn.cursor()
    railway_cursor = railway_conn.cursor()
    
    for table in tables_order:
        try:
            # Obtener datos de la tabla local
            local_cursor.execute(f"SELECT * FROM {table}")
            rows = local_cursor.fetchall()
            
            if not rows:
                print(f"⚠️ Tabla {table} está vacía")
                continue
            
            # Preparar INSERT para Railway
            columns = list(rows[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Insertar datos
            for row in rows:
                values = [row[col] for col in columns]
                railway_cursor.execute(insert_sql, values)
            
            railway_conn.commit()
            print(f"✅ {len(rows)} registros migrados en {table}")
            
        except Exception as e:
            print(f"❌ Error migrando {table}: {e}")
    
    local_conn.close()
    railway_conn.close()

def main():
    print("🚀 Iniciando migración de base de datos a Railway")
    print("=" * 50)
    
    # Verificar que tenemos las variables de entorno
    if not all([RAILWAY_DB['host'], RAILWAY_DB['user'], RAILWAY_DB['password']]):
        print("❌ Faltan variables de entorno de Railway")
        print("Configura: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")
        return
    
    # Probar conexiones
    if not test_connections():
        return
    
    # Crear estructura
    create_tables_in_railway()
    
    # Migrar datos
    migrate_data()
    
    print("=" * 50)
    print("🎉 Migración completada!")
    print("Tu aplicación en Railway ya debería funcionar con los datos.")

if __name__ == "__main__":
    main()
