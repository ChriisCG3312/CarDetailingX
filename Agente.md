# Contexto para IA — CarDetailingX

Eres un asistente de desarrollo para el proyecto **CarDetailingX**, 
una aplicación Django 5 + PostgreSQL para gestión de un taller de detailing automotriz.

## Stack
- Django 5.0.6, Python 3.12+
- PostgreSQL con psycopg2-binary
- Bootstrap 5.3 + Bootstrap Icons
- django-widget-tweaks para forms en templates
- python-decouple para variables de entorno

## Estructura de apps
- `apps/usuarios/`    — CustomUser con roles (admin, cliente, tecnico)
- `apps/servicios/`   — Servicio, Promocion
- `apps/citas/`       — Vehiculo, Cita, Pago
- `apps/seguimiento/` — Seguimiento, Notificacion

## Convenciones obligatorias

### Vistas
- Usar siempre Class-Based Views (ListView, CreateView, UpdateView, DeleteView)
- Nunca vistas funcionales salvo casos muy simples (redirects, acciones POST rápidas)
- Proteger con mixins de `apps.usuarios.mixins`: AdminRequiredMixin, TecnicoRequiredMixin, ClienteRequiredMixin

### Modelos
- Todos los FK usan `on_delete=models.PROTECT`
- Siempre definir `class Meta` con `verbose_name`, `verbose_name_plural` y `ordering`
- Siempre definir `__str__`

### Templates
- Todos extienden `base.html` con `{% extends "base.html" %}`
- Usar el partial `{% include "partials/_form_card.html" %}` para formularios
- Clases de Bootstrap 5 para todo el UI, sin CSS inline
- Los selects usan `form-select`, inputs usan `form-control`, checkboxes usan `form-check-input`

### Formularios
- Siempre definir widgets con clases Bootstrap en el `Meta` del ModelForm
- Validaciones de negocio van en el método `clean()` del form, no en la vista

### Commits
- Formato: `tipo(modulo): descripción`  
  Ejemplos: `feat(citas): agregar vista de cancelación`, `fix(servicios): corregir validación de fechas`

### Calidad
- Sin lógica de negocio en templates (solo presentación)
- Sin queries en templates (todo el contexto viene de la vista)
- Los mensajes de éxito/error siempre con `messages.success()` / `messages.error()`
- Comentarios en español

### Seguridad
- Nunca usar `redirect('/ruta/hardcodeada/')`, siempre `redirect('namespace:name')`
- Los nombres de URL siguen el patrón: `lista`, `crear`, `editar`, `eliminar`
- Nunca exponer datos de otros usuarios: siempre filtrar por `request.user`
  cuando el rol es cliente o tecnico
- Todo POST debe tener `{% csrf_token %}`
- Las vistas que modifican datos solo aceptan POST, nunca GET

## Restricciones para la IA
- No agregar dependencias nuevas a requirements.txt sin avisar al equipo
- No modificar `config/settings.py` ni `config/urls.py` sin consenso
- No cambiar modelos de otra app — si necesitas un campo nuevo en un modelo
  ajeno, abrir issue en GitHub y coordinarlo con el responsable
- No generar migraciones automáticamente — solo el código del modelo,
  el dev corre makemigrations manualmente


## Cómo usar este archivo
Pega el contenido de AGENTE.md + el archivo relevante de tu módulo 
y describe la tarea. Ejemplo:
"Aquí está el contexto del proyecto y mi models.py actual. 
Necesito la vista ListView para Citas con filtro por estado."