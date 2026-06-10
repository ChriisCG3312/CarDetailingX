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

    @property
    def precio_con_promocion(self):
        """Retorna el precio después de aplicar la promoción vigente, si existe."""
        promo = self.promociones.filter(
            activa=True,
            fecha_inicio__lte=timezone.now().date(),
            fecha_fin__gte=timezone.now().date(),
        ).first()
        if promo:
            descuento = self.precio * (promo.descuento_pct / 100)
            return round(self.precio - descuento, 2)
        return self.precio


class Promocion(models.Model):
    """Descuento temporal sobre un servicio específico."""

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name='promociones',
        verbose_name='Servicio',
    )
    descripcion = models.CharField(
        max_length=200, blank=True, verbose_name='Descripción de la promo'
    )
    descuento_pct = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name='Descuento (%)',
        help_text='Porcentaje de descuento (ej: 15 para 15%)'
    )
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_fin = models.DateField(verbose_name='Fecha de fin')
    activa = models.BooleanField(default=True, verbose_name='Activa')

    class Meta:
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.servicio.nombre} - {self.descuento_pct}% ({self.fecha_inicio} → {self.fecha_fin})'

    @property
    def esta_vigente(self):
        hoy = timezone.now().date()
        return self.activa and self.fecha_inicio <= hoy <= self.fecha_fin
