# VerdeQR - Documentación Técnica Completa 🌳

## 📋 Resumen Ejecutivo

**VerdeQR** es una aplicación web educativa que funciona como "un dendrólogo en tu bolsillo". Permite a los usuarios identificar y aprender sobre árboles silvestres mediante códigos QR, proporcionando información científica detallada sobre especies, características, usos y curiosidades.

## 🏗️ Arquitectura del Sistema

### Stack Tecnológico

**Backend:**
- **Framework**: Flask 2.3.2 (Python)
- **Base de Datos**: MySQL con PyMySQL 1.1.0
- **ORM**: Consultas SQL nativas (sin ORM)
- **Servidor**: Gunicorn 21.2.0 para producción

**Frontend:**
- **Templates**: Jinja2 2.1.2
- **Estilos**: CSS3 puro con diseño responsive
- **JavaScript**: Vanilla JS para interactividad
- **QR Scanner**: jsQR library para lectura de códigos

**Funcionalidades Especiales:**
- **Generación QR**: qrcode 7.4.2 + Pillow 10.1.0
- **Email**: Flask-Mail 0.9.1 para recuperación de contraseñas
- **Gestión de archivos**: Subida y procesamiento de imágenes

### Patrón de Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Base de       │
│   (Templates)   │◄──►│    (Flask)      │◄──►│   Datos (MySQL) │
│                 │    │                 │    │                 │
│ • HTML/CSS/JS   │    │ • Rutas         │    │ • 20+ Tablas    │
│ • QR Scanner    │    │ • Lógica        │    │ • Relaciones    │
│ • Responsive    │    │ • Autenticación │    │ • Integridad    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🗄️ Estructura de Base de Datos

### Tablas Principales

**Entidades Core:**
- `Usuario` - Gestión de usuarios y autenticación
- `Especie` - Información científica de especies arbóreas
- `Arbol` - Instancias específicas de árboles registrados
- `Centro` - Ubicaciones donde se encuentran los árboles
- `CodigoQR` - Códigos QR generados para cada árbol

**Clasificación y Características:**
- `TipoBosque` - Tipos de ecosistemas forestales
- `UsoArbol` - Categorización de usos (medicinal, maderable, etc.)
- `CuriosidadesArbol` - Datos interesantes sobre especies
- `InteraccionesEcologicas` - Relaciones ecológicas

**Usos Especializados (11 tablas):**
- `UsoMedicinal`, `UsoComestible`, `UsoMaderable`
- `UsoOrnamental`, `UsoArtesanal`, `UsoAgroforestal`
- `UsoRestauracionEcologica`, `UsoCulturalCeremonial`
- `UsoMelifero`, `UsoProteccionAmbiental`, `UsoTintoreo`
- `UsoOleaginoso`, `UsoBiocombustible`

**Sistema de Soporte:**
- `Estado` - Estados de activación/desactivación
- `Rol` - Roles de usuario (Administrador, Visitante)
- `UsuarioRol` - Relación muchos a muchos usuarios-roles
- `tokens_recuperacion` - Tokens para recuperación de contraseñas
- `sugerencias` - Sistema de feedback de usuarios

### Relaciones Clave

```sql
Especie (1) ──── (N) Arbol ──── (1) Centro
   │                │
   │                └── (1) TipoBosque
   │
   └── (N) UsoArbol ──── (1) UsoEspecifico
```

## 🔧 Funcionalidades Principales

### 1. Sistema de Autenticación
- **Registro de usuarios** con validación de contraseñas
- **Inicio de sesión** con roles diferenciados
- **Recuperación de contraseñas** vía email con tokens temporales
- **Gestión de sesiones** con Flask sessions

### 2. Gestión de Árboles
- **CRUD completo** para árboles, especies y centros
- **Subida de imágenes** con procesamiento automático
- **Generación automática de QR** para cada árbol
- **Búsqueda avanzada** por múltiples criterios

### 3. Sistema QR
- **Generación automática** de códigos QR únicos
- **Scanner web** usando cámara del dispositivo
- **Información detallada** al escanear códigos

### 4. Panel de Administración
- **Dashboard principal** con estadísticas
- **Gestión de usuarios** y roles
- **Administración de contenido** (especies, usos, curiosidades)
- **Sistema de sugerencias** de usuarios

### 5. Características Técnicas
- **Responsive design** optimizado para móviles
- **Paginación** para grandes volúmenes de datos
- **Validación de datos** en frontend y backend
- **Manejo de errores** robusto
- **Limpieza de texto UTF-8** para caracteres especiales

## 📁 Estructura del Proyecto

```
VerdeQR_Nuevo/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias Python
├── schema.sql            # Esquema de base de datos
├── Procfile              # Configuración para despliegue
├── railway.json          # Configuración Railway.app
├── README.md             # Documentación básica
├── static/               # Archivos estáticos
│   ├── css/             # Hojas de estilo
│   ├── js/              # Scripts JavaScript
│   └── uploads/         # Imágenes subidas
├── templates/           # Plantillas HTML
│   ├── base.html        # Plantilla base
│   ├── inicio.html      # Página de inicio
│   ├── principal.html   # Dashboard principal
│   └── [40+ templates]  # Plantillas específicas
└── venv/               # Entorno virtual Python
```

## 🚀 Configuración y Despliegue

### Desarrollo Local

```bash
# 1. Clonar repositorio
git clone [repositorio]
cd VerdeQR_Nuevo

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos
# Crear BD MySQL 'VerdeQR'
# Importar schema.sql

# 5. Ejecutar aplicación
python app.py
```

### Producción (Railway.app)

El proyecto está configurado para despliegue automático en Railway.app:

**Variables de entorno requeridas:**
```
DATABASE_URL=mysql://user:pass@host:port/db
SECRET_KEY=clave_secreta_segura
MAIL_USERNAME=correo@gmail.com
MAIL_PASSWORD=clave_aplicacion
```

**Archivos de configuración:**
- `Procfile`: `web: gunicorn app:app`
- `railway.json`: Configuración de build y deploy
- `requirements.txt`: Dependencias exactas

## 🔒 Seguridad

### Medidas Implementadas
- **Validación de contraseñas**: Mínimo 8 caracteres + mayúscula
- **Sanitización de datos**: Limpieza de caracteres UTF-8 problemáticos
- **Gestión de sesiones**: Flask sessions seguras
- **Tokens temporales**: Para recuperación de contraseñas (30 min)
- **Validación de archivos**: Procesamiento seguro de imágenes
- **SQL preparado**: Prevención de inyección SQL

### Roles y Permisos
- **Administrador**: Acceso completo al sistema
- **Visitante**: Acceso de solo lectura
- **Sistema de roles**: Extensible para nuevos permisos

## 📱 Características de UX/UI

### Diseño Responsive
- **Mobile-first**: Optimizado para dispositivos móviles
- **CSS Grid/Flexbox**: Layout moderno y flexible
- **Breakpoints**: Adaptación a diferentes tamaños de pantalla

### Interactividad
- **Scanner QR**: Acceso directo desde cámara
- **Búsqueda en tiempo real**: Autocompletado y filtros
- **Notificaciones**: Sistema de mensajes flash
- **Carrusel de imágenes**: Navegación visual atractiva

## 🔄 Flujo de Datos Principal

```
Usuario escanea QR → Aplicación lee código → 
Consulta BD por ID árbol → Obtiene información completa →
Muestra datos: especie, características, usos, curiosidades
```

## 📊 Métricas y Estadísticas

El sistema incluye dashboard con:
- Total de árboles registrados
- Número de usuarios activos
- Centros disponibles
- Sugerencias recientes

## 🔮 Escalabilidad y Futuras Mejoras

### Arquitectura Preparada Para:
- **API REST**: Estructura modular permite fácil conversión
- **Microservicios**: Separación clara de responsabilidades
- **Cache**: Implementación de Redis para optimización
- **CDN**: Para servir imágenes estáticamente

### Posibles Extensiones:
- App móvil nativa
- Geolocalización de árboles
- Sistema de favoritos
- Comunidad de usuarios
- Machine Learning para identificación automática

## 💻 Detalles de Implementación

### Rutas Principales del Sistema

**Autenticación:**
- `GET/POST /registro` - Registro de nuevos usuarios
- `GET/POST /iniciar_sesion` - Autenticación de usuarios
- `GET /cerrar_sesion` - Cierre de sesión
- `GET/POST /olvidar_contrasena` - Solicitud de recuperación
- `GET/POST /restablecer_contrasena` - Cambio de contraseña con token

**Navegación Principal:**
- `GET /` - Página de inicio pública
- `GET /principal` - Dashboard principal (requiere login)
- `GET /todos_los_arboles` - Listado paginado de árboles
- `GET /buscar_arbol` - Búsqueda avanzada con filtros

**Gestión de Datos (CRUD):**
- `GET/POST /arbol` - Gestión de árboles
- `GET/POST /arbol/editar/<id>` - Edición de árboles
- `GET /arbol/eliminar/<id>` - Eliminación de árboles
- `GET/POST /especie` - Gestión de especies
- `GET/POST /centro` - Gestión de centros

**Funcionalidades Especiales:**
- `GET/POST /qr` - Generación y gestión de códigos QR
- `GET /ver_qr/<id>` - Visualización de QR específico
- `GET /ver_arbol/<id>` - Información detallada de árbol

### Funciones Utilitarias Clave

```python
def get_base_url()
    """Detecta automáticamente la URL base (localhost/túnel/dominio)"""

def limpiar_texto_utf8(texto)
    """Limpia caracteres problemáticos UTF-8"""

def determinar_genero(nombre)
    """Determina género para avatar predeterminado"""

def generar_token(longitud=6)
    """Genera tokens aleatorios para recuperación"""
```

### Configuración de Base de Datos

```python
def get_db_config():
    """Configuración automática para desarrollo/producción"""
    # Detecta DATABASE_URL (Railway) o variables separadas (local)
    # Retorna configuración PyMySQL con charset utf8mb4
```

### Manejo de Imágenes

- **Subida**: Validación y renombrado automático con timestamp
- **Almacenamiento**: `static/css/js/img/` para compatibilidad
- **Procesamiento**: Pillow para manipulación de imágenes
- **Rutas**: Normalización de barras para compatibilidad cross-platform

### Sistema de Paginación

```python
# Implementación en /todos_los_arboles
page = request.args.get('page', 1, type=int)
per_page = 10
offset = (page - 1) * per_page

# Cálculo de metadatos de paginación
total_pages = (total_arboles + per_page - 1) // per_page
has_prev = page > 1
has_next = page < total_pages
```

## 🔍 Características Técnicas Avanzadas

### Búsqueda Inteligente

El sistema implementa búsqueda en múltiples niveles:

1. **Búsqueda exacta** por ID de especie/centro
2. **Búsqueda por texto** en múltiples campos:
   - Nombre científico y vulgar
   - Características del árbol
   - Servicios ecosistémicos
   - Descripción general
3. **Búsqueda parcial** por palabras clave (>3 caracteres)

### Generación de QR

```python
# Proceso automático al registrar árbol
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(f"{base_url}/ver_arbol/{arbol_id}")
qr.make(fit=True)

# Conversión a base64 para almacenamiento
img_buffer = io.BytesIO()
qr_img.save(img_buffer, format='PNG')
qr_base64 = base64.b64encode(img_buffer.getvalue()).decode()
```

### Sistema de Estados

Todas las entidades principales manejan estados:
- `1` = Activo
- `2` = Inactivo/Usado (tokens)
- Permite "eliminación suave" manteniendo integridad referencial

### Validaciones Implementadas

**Frontend (JavaScript):**
- Validación en tiempo real de formularios
- Confirmación de eliminaciones
- Validación de archivos de imagen

**Backend (Python):**
- Regex para contraseñas: `^(?=.*[A-Z]).{8,}$`
- Validación de correos únicos
- Sanitización de datos UTF-8
- Verificación de tokens temporales

## 🌐 Configuración de Despliegue

### Variables de Entorno

```bash
# Desarrollo Local
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=VerdeQR
SECRET_KEY=desarrollo_key

# Producción Railway
DATABASE_URL=mysql://user:pass@host:port/db
SECRET_KEY=production_key_muy_segura
MAIL_USERNAME=verdeqr.app@gmail.com
MAIL_PASSWORD=app_specific_password
```

### Configuración de Email

```python
# Flask-Mail configuración
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_SUPPRESS_SEND = True  # Para desarrollo
```

### Optimizaciones de Producción

- **Gunicorn**: Servidor WSGI para producción
- **Conexiones DB**: Pool de conexiones con PyMySQL
- **Manejo de errores**: Try-catch comprehensivo
- **Logging**: Impresión de errores para debugging

## 📈 Métricas de Rendimiento

### Consultas Optimizadas

- **JOINs eficientes**: LEFT JOIN para datos relacionados
- **Índices**: Claves foráneas automáticamente indexadas
- **Paginación**: LIMIT/OFFSET para grandes datasets
- **Agregaciones**: COUNT() para estadísticas

### Carga de Archivos

- **Validación**: Extensiones y tamaños permitidos
- **Almacenamiento**: Estructura organizada por tipo
- **Nombres únicos**: Timestamp + nombre original

## 🔧 Mantenimiento y Debugging

### Logs del Sistema

```python
# Información de conexión DB
print("Conexión a la base de datos establecida correctamente")

# Debugging de sesiones
print(f"Sesión de usuario creada: {session['usuario']}")

# Errores con traceback completo
import traceback
print(traceback.format_exc())
```

### Estructura de Errores

- **Flash messages**: Notificaciones al usuario
- **JSON responses**: Para peticiones AJAX
- **Rollback automático**: En transacciones fallidas
- **Redirecciones**: Manejo de estados de error

---

**Desarrollado con ❤️ para la educación ambiental y la conservación forestal**

## 📞 Información de Contacto Técnico

**Proyecto**: VerdeQR - Un dendrólogo en tu bolsillo
**Tecnologías**: Flask + MySQL + QR + Responsive Design
**Despliegue**: Railway.app con auto-deploy desde GitHub
**Licencia**: MIT License
