from django.contrib import admin
from .models import Servicio, Promocion, Paquete


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion_horas', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    list_editable = ('activo',)

@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'paquete', 'descuento_pct', 'fecha_inicio', 'fecha_fin', 'activa')
    list_filter = ('activa', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre', 'paquete__nombre')

@admin.register(Paquete)
class PaqueteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'es_personalizado', 'activo', 'creado_en')
    list_filter = ('activo', 'es_personalizado')
    search_fields = ('nombre', 'descripcion')
    # Esto hará que los servicios se seleccionen con una interfaz de doble cuadro muy cómoda:
    filter_horizontal = ('servicios',)