# VerdeQR - Un dendrólogo en tu bolsillo 🌳

Aplicación web para identificar árboles silvestres mediante códigos QR, desarrollada con Flask y MySQL.

## 🚀 Características

- **Identificación por QR**: Escanea códigos QR para obtener información detallada de árboles
- **Base de datos completa**: Información científica de especies, características y usos
- **Gestión de usuarios**: Sistema de registro y autenticación
- **Panel de administración**: Gestión completa de árboles, especies y centros
- **Responsive**: Optimizado para dispositivos móviles
- **Paginación**: Visualización eficiente de grandes cantidades de datos

## 🛠️ Tecnologías

- **Backend**: Flask (Python)
- **Base de datos**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript
- **QR**: Generación automática de códigos QR
- **Responsive**: CSS Grid y Flexbox

## 📦 Instalación Local

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/verdeqr.git
cd verdeqr
```

2. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configura la base de datos:
- Crea una base de datos MySQL llamada `verdeqr`
- Importa el archivo `schema.sql`
- Configura las credenciales en `app.py`

5. Ejecuta la aplicación:
```bash
python app.py
```

## 🌐 Despliegue en Railway.app

Este proyecto está configurado para desplegarse automáticamente en Railway.app:

### Pasos para el despliegue:

1. **Sube tu código a GitHub**
2. **Ve a [railway.app](https://railway.app)** y regístrate con GitHub
3. **New Project** → **Deploy from GitHub repo** → Selecciona tu repositorio
4. **Railway detectará automáticamente** Flask y configurará todo
5. **Agrega una base de datos MySQL** desde el dashboard
6. **Configura las variables de entorno** (ver sección abajo)
7. **Deploy** → ¡Tu aplicación estará en línea!

### Variables de entorno en Railway:
```
DB_HOST=${{MySQL.MYSQL_HOST}}
DB_USER=${{MySQL.MYSQL_USER}}
DB_PASSWORD=${{MySQL.MYSQL_PASSWORD}}
DB_NAME=${{MySQL.MYSQL_DATABASE}}
SECRET_KEY=tu_clave_secreta_muy_segura
FLASK_ENV=production
```

**Nota:** Railway auto-genera las variables de MySQL cuando agregas el servicio.

## 📱 Uso

1. **Registro**: Crea una cuenta de usuario
2. **Explorar**: Navega por los árboles disponibles
3. **Escanear QR**: Usa la cámara para escanear códigos QR de árboles
4. **Aprender**: Descubre información detallada sobre cada especie

## 🔧 Configuración

### Variables de Entorno (Render.com)

- `DB_HOST`: Host de la base de datos
- `DB_USER`: Usuario de la base de datos  
- `DB_PASSWORD`: Contraseña de la base de datos
- `DB_NAME`: Nombre de la base de datos
- `SECRET_KEY`: Clave secreta de Flask
- `FLASK_ENV`: production

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 👥 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Contacto

- **Proyecto**: VerdeQR
- **Descripción**: Un dendrólogo en tu bolsillo
- **Tecnología**: Flask + MySQL + QR Codes
