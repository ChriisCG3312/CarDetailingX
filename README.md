# CarDetailingX
=======
# CarDetailingX — Sistema de Gestión

Aplicación web Django + PostgreSQL para la gestión de un taller de detailing automotriz.

---

## Estructura del proyecto

```
detailing_project/
├── apps/
│   ├── usuarios/       # D1 — Auth, CustomUser, Clientes
│   ├── servicios/      # D2 — Catálogo, Promociones
│   ├── citas/          # D3 — Vehículos, Agenda, Pagos
│   └── seguimiento/    # D4 — Tracking, Notificaciones
├── config/             # settings.py, urls.py, wsgi.py
├── static/             # CSS, JS, imágenes globales
├── templates/          # base.html, dashboard, partials
├── manage.py
├── requirements.txt
└── .env.example
```

---

## Setup inicial (todos los integrantes)

### 1. Clonar el repositorio

Dentro de la carpeta que usarás para el proyecto:

```bash
cd ruta/tu_carpeta
git init
git clone https://github.com/ChriisCG3312/CarDetailingX.git
```

### Iniciar tu rama de trabajo

```bash
git checkout -b develop
git remote add origin https://github.com/ChriisCG3312/CarDetailingX.git
git pull origin develop
git checkout -b feature/tu-modulo
```

Tus archivos deberían de haber cambiado, sino, informa al dueño del repositorio.

### 2. Crear y activar entorno virtual

```bash
# Windows
python -m venv env
.\env\Scripts\activate
```

### 3. Instalar dependencias

```bash
# Asegúrate de tener Python 3.12
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# COPIA LA ESTRUCTURA DE .example y EDITA .env
copy .env.example .env
# edita con tu DB_NAME, DB_USER, DB_PASSWORD

```

### 5. Crear la base de datos en PostgreSQL

```sql
CREATE DATABASE CarDetailingX;
```

### 6. Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crear superusuario (Admin)

```bash
python manage.py createsuperuser
```

### 8. Correr el servidor

```bash
python manage.py runserver
```

Accede en: http://127.0.0.1:8000/

---

### Convención de commits

```
feature/(modulo): descripción breve
fix/(modulo): corrección
docs/(readme): actualización
refactor/(views): mejora de código
test/(modulo): prueba unitaria
```
### Guardar de forma local los cambios
1. Agrega todos tus cambios: `git add .`
2. Comprueba tus archivos con `git status`
2. Haz commit local. Recuerda mantener la convención de commits: `git commit -m "(tu mensaje)` 

### Subir a GitHub
1. Asegúrate de estar en la rama correspondiente
2. Haz commit de tus cambios
3. Haz push a tu rama en github: `git push origin feature/(tu-modulo)`

### Crear Pull Request a Develop

1. Sube los cambios a tu rama: `git push origin feature/tu-modulo`
2. Abre PR hacia `develop` EN GITHUB
3. Añade descripción + instrucciones para probar
4. Mínimo 1 revisión aprobada antes de mergear

---

## Módulos y responsables

| App | Responsable | Modelos principales |
|-----|-------------|---------------------|
| `usuarios` | Christian | `Usuario` (CustomUser) |
| `servicios` | Manuel | `Servicio`, `Promocion` |
| `citas` | Carlos | `Vehiculo`, `Cita`, `Pago` |
| `seguimiento` | Brayan | `Seguimiento`, `Notificacion` |

---

## Partial de formulario reutilizable

```django
{% include "partials/_form_card.html" with form=form titulo="Nuevo registro" cancel_url="app:lista" %}
```

---

## Panel de administración Django

```
http://127.0.0.1:8000/admin/
```

Todos los modelos están registrados en su respectivo `admin.py`.

