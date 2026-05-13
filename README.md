# 🏋️ Monster Gym - Sistema de Gestión de Gimnasio

Aplicación web para la administración integral de un gimnasio. Permite gestionar inventario, máquinas, usuarios, personal, distribuidores y notificaciones, con **autenticación JWT** mediante cookies y **control de acceso basado en roles** (Admin, Recepcionista, Cliente, Entrenador, Distribuidor).

## ✨ Características principales

- 🔐 **Autenticación segura** con JWT (cookies HttpOnly) y contraseñas hasheadas (Werkzeug/bcrypt).
- 👥 **Roles y permisos**:
  - **Admin**: acceso total a todos los módulos.
  - **Recepcionista**: puede ver/registrar/editar usuarios (solo clientes), y gestionar máquinas.
  - **Cliente**: acceso a su perfil y notificaciones.
  - **Entrenador / Distribuidor**: roles adicionales.
- 🗃️ **Base de datos dual**:
  - **MySQL**: usuarios, inventario, máquinas, miembros, personal, distribuidores.
  - **MongoDB**: notificaciones y actividades.
- 📦 **Módulos incluidos**:
  - Inventario de productos (CRUD).
  - Máquinas del gimnasio (CRUD).
  - Usuarios (clientes) con membresías.
  - Personal (empleados con salario y fecha contratación).
  - Distribuidores (con categoría).
  - Notificaciones (integración con MongoDB).
- 📄 **Interfaz responsive** con Bootstrap 5.
- 🐍 **Backend**: Flask + Flask-JWT-Extended + PyMongo + mysql-connector-python.

## 🗂️ Tecnologías utilizadas

- Python 3.12+
- Flask 3.1.2
- Flask-JWT-Extended 4.6.0
- MySQL 8.0
- MongoDB 7.0+
- Bootstrap 5 (frontend)
- Werkzeug (hashing de contraseñas)
- PyMongo, mysql-connector-python

## 📥 Instalación y configuración

### Requisitos previos

- Python 3.12 o superior
- MySQL Server (8.0+)
- MongoDB Server (7.0+)
- pip y virtualenv (recomendado)

### Pasos para levantar el proyecto

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/monster-gym.git
   cd monster-gym
2. Crear y activar entorno virtual

python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

3. Instalar dependencias

pip install -r requirements.txt

4. Configurar la base de datos MySQL

Crear una base de datos llamada monster gym (con espacio).

Importar el archivo bd_monster_gym.sql (incluido en el repositorio).

Verificar que las credenciales en app.py coincidan con tu instalación (usuario root, contraseña 12345 por defecto). Ajusta si es necesario.

5. Configurar MongoDB

Asegurar que MongoDB esté corriendo en localhost:27017.

La base de datos monster_gym y la colección notificaciones se crearán automáticamente al primer uso.

6. Ejecutar la aplicación

python app.py

7. Acceder al sistema

URL: http://localhost:5000

Usuario administrador por defecto (creado automáticamente si no existe):

Usuario: admin

Contraseña: admin123

🔐 Estructura de roles y permisos
Módulo	Admin	Recepcionista	Cliente
Inventario (CRUD)	✅	❌	❌
Máquinas (CRUD)	✅	✅	❌
Usuarios (listado)	✅ (todos)	✅ (solo clientes)	❌
Registrar usuario	✅ (cualquier rol)	✅ (solo clientes)	❌
Editar usuario	✅	✅ (solo clientes)	❌
Eliminar usuario	✅	❌	❌
Personal (empleados)	✅	❌	❌
Distribuidores	✅	❌	❌
Notificaciones	✅ (todas)	✅ (propias)	✅ (propias)
📁 Estructura del proyecto
text
monster-gym/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias Python
├── bd_monster_gym.sql     # Script de la base de datos MySQL
├── templates/             # Plantillas HTML
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── inventario.html
│   ├── maquinas.html
│   ├── usuarios.html
│   ├── personal.html
│   ├── distribuidores.html
│   └── ... (editar, registrar)
└── README.md
📌 Notas importantes
Seguridad: En producción, cambiar JWT_SECRET_KEY, SECRET_KEY y usar JWT_COOKIE_SECURE = True (requiere HTTPS).

MongoDB: Las notificaciones se almacenan como documentos JSON; puedes extender el modelo fácilmente.

Roles adicionales: Puedes añadir más roles en la tabla rol y adaptar los decoradores.

Reportes: El sistema se puede extender con generación de reportes (ventas, membresías activas, etc.).
