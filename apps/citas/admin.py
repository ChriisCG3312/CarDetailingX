from django.contrib import admin
from .models import Vehiculo, Cita, Pago


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placas', 'marca', 'modelo', 'anio', 'color', 'cliente')
    search_fields = ('placas', 'marca', 'modelo', 'cliente__last_name')
    list_filter = ('marca',)


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'vehiculo', 'paquete', 'fecha_hora', 'estado')
    list_filter = ('estado',)
    search_fields = ('cliente__last_name', 'vehiculo__placas')
    date_hierarchy = 'fecha_hora'
    readonly_fields = ('creada_en', 'actualizada_en')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cita', 'monto', 'metodo', 'pagado_en')
    list_filter = ('metodo',)