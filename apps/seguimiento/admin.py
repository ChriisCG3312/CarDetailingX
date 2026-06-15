from django.contrib import admin
from .models import Seguimiento, Notificacion


@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display  = ('cita', 'tecnico', 'estado', 'actualizado_en')
    list_filter   = ('estado',)
    search_fields = ('cita__cliente__last_name', 'tecnico__last_name')
    readonly_fields = ('creado_en', 'actualizado_en')


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'tipo', 'leida', 'creada_en')
    list_filter   = ('tipo', 'leida')
    search_fields = ('usuario__last_name', 'mensaje')
    readonly_fields = ('creada_en',)