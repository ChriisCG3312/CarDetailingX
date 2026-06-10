# CarDetailingX
=======
# Detailing Pro — Sistema de Gestión

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

Dentro de la carpeta que usarás para el proyecto

```bash
cd ruta/tu_carpeta
git clone https://github.com/ChriisCG3312/CarDetailingX.git
```

### 2. Crear y activar entorno virtual

```bash
# Windows
python -m venv env
.\env\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Abre .env y edita los valores de DB_NAME, DB_USER, DB_PASSWORD
# Usa tu propia base de datos. No se usarán en el repositorio final.
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

## Flujo de trabajo Git

| Rama | Propósito |
|------|-----------|
| `main` | Producción — solo merge desde develop |
| `develop` | Integración — todos los PR van aquí |
| `feature/usuarios-auth` | Módulo D1 |
| `feature/servicios-promo` | Módulo D2 |
| `feature/citas-pago` | Módulo D3 |
| `feature/seguimiento-notif` | Módulo D4 |

### Iniciar tu rama de trabajo

```bash
git checkout develop
git pull origin develop
git checkout -b feature/tu-modulo
```

### Convención de commits

```
feature/(modulo): descripción breve
fix/(modulo): corrección
docs/(readme): actualización
refactor/(views): mejora de código
test/(modulo): prueba unitaria
```

### Crear Pull Request

1. Push a tu rama: `git push origin feature/tu-modulo`
2. Abre PR hacia `develop` en GitHub
3. Añade descripción + instrucciones para probar
4. Mínimo 1 revisión aprobada antes de mergear

> ⚠️ **Importante con migraciones:** D1 debe mergear `CustomUser` primero.
> Antes de crear migraciones que dependan de otro módulo, sincroniza con `develop`.

---

## Módulos y responsables

| App | Responsable | Modelos principales |
|-----|-------------|---------------------|
| `usuarios` | D1 | `Usuario` (CustomUser) |
| `servicios` | D2 | `Servicio`, `Promocion` |
| `citas` | D3 | `Vehiculo`, `Cita`, `Pago` |
| `seguimiento` | D4 | `Seguimiento`, `Notificacion` |

---

## Mixins de permisos (disponibles para todos)

```python
from apps.usuarios.mixins import AdminRequiredMixin, TecnicoRequiredMixin, ClienteRequiredMixin

class MiVista(AdminRequiredMixin, ListView):
    ...
```

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

