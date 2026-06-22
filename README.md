# CarDetailingX — Sistema de Gestión para Taller de Detailing Automotriz

Aplicación web desarrollada con **Python 3.12.x**, **Django 5.0.6** y **PostgreSQL**, diseñada para la administración integral de un taller de detailing automotriz.

El sistema permite gestionar:

* Usuarios y roles
* Servicios y promociones
* Vehículos
* Citas
* Reportes
* Pagos
* Seguimiento de servicios
* Notificaciones
* Panel administrativo

---

# Tecnologías utilizadas

| Tecnología | Versión |
| ---------- | ------- |
| Python     | 3.12.x  |
| Django     | 5.0.6   |
| PostgreSQL | 15+     |
| HTML5      | Última  |
| CSS3       | Última  |
| Bootstrap  | 5.x     |
| JavaScript | ES6+    |

---

# Estructura del proyecto

```text
detailing_project/
├── apps/
│   ├── usuarios/
│   ├── servicios/
│   ├── citas/
│   ├── repotes/
│   └── seguimiento/
├── config/
├── static/
├── templates/
├── manage.py
├── requirements.txt
└── .env.example
```

---

# Instalación del proyecto

## Opción 1: Crear un Fork (Recomendado para estudiantes)

Si deseas modificar o mejorar el proyecto sin afectar el repositorio original:

### 1. Realiza un Fork

En GitHub:

1. Abre el repositorio original. " https://github.com/ChriisCG3312/CarDetailingX.git "
2. Haz clic en **Fork**.
3. Selecciona tu cuenta.
4. Espera a que GitHub cree tu copia.

---

### 2. Clona tu Fork

```bash
git clone https://github.com/TU_USUARIO/CarDetailingX.git
git remote add origin https://github.com/TU_USUARIO/CarDetailingX.git
cd CarDetailingX
```

---

# Configuración del entorno

## 1. Crear entorno virtual

### Windows

```bash
python -m venv env

env\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv env

source env/bin/activate
```

---

## 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 3. Configurar variables de entorno

Crear el archivo `.env` utilizando como base `.env.example`.

### Windows

```bash
copy .env.example .env
```

### Linux / macOS

```bash
cp .env.example .env
```

Editar los valores correspondientes:

```env
DB_NAME=CarDetailingX
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

---

# Configuración de PostgreSQL

## Crear la base de datos

```sql
CREATE DATABASE CarDetailingX;
```

---

# Despliegue local

## Aplicar migraciones

```bash
python manage.py makemigrations

python manage.py migrate
```

---

## Crear usuario administrador

```bash
python manage.py createsuperuser
```

---

## Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

Abrir en el navegador:

```text
http://127.0.0.1:8000/
```

---

# Acceso al panel administrativo

```text
http://127.0.0.1:8000/admin/
```

Todos los modelos del sistema se encuentran registrados en el panel de administración de Django.

---

# Flujo de trabajo recomendado con Git

## Crear una nueva rama

```bash
git checkout -b nueva-funcionalidad
```

---

## Guardar cambios localmente

```bash
git add .

git commit -m "descripcion breve"
```

---

## Subir cambios

```bash
git push origin nueva-funcionalidad
```


## Si necesitas cambiar de rama sin crear una nueva

```bash
git checkout tu-rama-destino
```


---

# Convención de commits

```text
feature(modulo): nueva funcionalidad
fix(modulo): corrección de errores
docs(readme): actualización de documentación
refactor(modulo): mejora interna del código
test(modulo): pruebas
```

---

# Módulos del sistema

| Aplicación  | Función                                    |
| ----------- | ------------------------------------------ |
| usuarios    | Gestión de usuarios y roles                |
| servicios   | Gestión de servicios y promociones         |
| citas       | Administración de vehículos, citas y pagos |
| seguimiento | Seguimiento de servicios y notificaciones  |
| reportes    | Visualización y exportación de datos relev.|

---

# Ejemplo de formulario reutilizable

```django
{% include "partials/_form_card.html" with form=form titulo="Nuevo registro" cancel_url="app:lista" %}
```

---

# Objetivo académico

Este proyecto fue desarrollado con fines académicos para demostrar la implementación de una arquitectura web basada en Django y PostgreSQL.

Se invita a estudiantes y desarrolladores a utilizar este repositorio como base de aprendizaje, realizar mejoras, implementar nuevas funcionalidades y aplicar buenas prácticas de desarrollo de software.
