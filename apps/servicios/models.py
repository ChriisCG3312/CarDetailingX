"""
Módulo: Servicios y Promociones
Responsable: D2

Modelos:
- Servicio: catálogo de servicios de detailing disponibles.
- Promocion: descuentos temporales vinculados a un servicio.
"""
from django.db import models
from django.utils import timezone


class Servicio(models.Model):
    """Servicio de detailing que ofrece el negocio."""

    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    precio = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Precio (MXN)'
    )
    duracion_horas = models.DecimalField(
        max_digits=4, decimal_places=1, verbose_name='Duración (horas)',
        help_text='Tiempo estimado del servicio en horas'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    imagen = models.ImageField(
        upload_to='servicios/', blank=True, null=True, verbose_name='Imagen'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} (${self.precio})'

class Paquete(models.Model):
    """Un paquete o combo que agrupa varios servicios individuales."""
    nombre = models.CharField(max_length=100, verbose_name='Nombre del Paquete') # Ej: Paquete 1, Paquete 2
    descripcion = models.TextField(blank=True, verbose_name='Descripción de lo que incluye')
    
    # Relación Muchos a Muchos: Un paquete tiene muchos servicios individuales
    servicios = models.ManyToManyField(Servicio, verbose_name='Servicios Incluidos')
    
    es_personalizado = models.BooleanField(default=False, verbose_name='¿Es personalizado por el cliente?')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Paquete'
        verbose_name_plural = 'Paquetes'

    def __str__(self):
        return self.nombre

    @property
    def precio_base(self):
        """Suma el precio normal de todos los servicios que integran el paquete."""
        return sum(servicio.precio for servicio in self.servicios.all())

    @property
    def precio_final(self):
        """Calcula el precio aplicando la promoción activa del paquete si existe."""
        promo = self.promociones.filter(
            activa=True,
            fecha_inicio__lte=timezone.now().date(),
            fecha_fin__gte=timezone.now().date(),
        ).first()
        if promo:
            descuento = self.precio_base * (promo.descuento_pct / 100)
            return round(self.precio_base - descuento, 2)
        return self.precio_base
    @property
    def duracion_total(self):
        return sum(servicio.duracion_horas for servicio in self.servicios.all())


class Promocion(models.Model):
    """Descuento temporal aplicado obligatoriamente a un paquete completo."""
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la promoción')
    
    # CAMBIO CLAVE: Ahora ForeignKey apunta a Paquete, ya no a Servicio
    paquete = models.ForeignKey(
        Paquete,
        on_delete=models.PROTECT,
        related_name='promociones',
        verbose_name='Paquete Asociado',
    )
    descripcion = models.CharField(max_length=200, blank=True, verbose_name='Descripción de la promo')
    descuento_pct = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Descuento (%)')
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_fin = models.DateField(verbose_name='Fecha de fin')
    activa = models.BooleanField(default=True, verbose_name='Activa')

    class Meta:
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.nombre} ({self.descuento_pct}% OFF)'