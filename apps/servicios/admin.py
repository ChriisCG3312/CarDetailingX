from django.contrib import admin
from .models import Servicio, Promocion


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion_horas', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    list_editable = ('activo',)


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'descuento_pct', 'fecha_inicio', 'fecha_fin', 'activa', 'esta_vigente')
    list_filter = ('activa',)
    readonly_fields = ('esta_vigente',)
