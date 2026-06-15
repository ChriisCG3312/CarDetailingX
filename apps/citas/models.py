"""
Módulo: Citas y Pagos
Responsable: D3

Modelos:
- Vehiculo: vehículo registrado por un cliente.
- Cita: cita agendada que vincula cliente, vehículo y servicio.
- Pago: registro del pago asociado a una cita.
"""
from django.db import models
from django.conf import settings
from apps.servicios.models import Servicio


class Vehiculo(models.Model):
    """Vehículo registrado por un cliente."""

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='vehiculos',
        verbose_name='Cliente',
        limit_choices_to={'rol': 'cliente'},
    )
    marca = models.CharField(max_length=50, verbose_name='Marca')
    modelo = models.CharField(max_length=50, verbose_name='Modelo')
    anio = models.PositiveSmallIntegerField(verbose_name='Año')
    color = models.CharField(max_length=30, verbose_name='Color')
    placas = models.CharField(max_length=10, unique=True, verbose_name='Placas')
    foto = models.ImageField(
        upload_to='vehiculos/', blank=True, null=True, verbose_name='Foto'
    )

    class Meta:
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        ordering = ['cliente__last_name', 'marca']

    def __str__(self):
        return f'{self.marca} {self.modelo} {self.anio} ({self.placas})'


class Cita(models.Model):
    """Cita agendada en el taller de detailing."""

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        CONFIRMADA = 'confirmada', 'Confirmada'
        EN_PROCESO = 'en_proceso', 'En proceso'
        TERMINADA = 'terminada', 'Terminada'
        CANCELADA = 'cancelada', 'Cancelada'

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='citas',
        verbose_name='Cliente',
        limit_choices_to={'rol': 'cliente'},
    )
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.PROTECT,
        related_name='citas',
        verbose_name='Vehículo',
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name='citas',
        verbose_name='Servicio',
    )
    fecha_hora = models.DateTimeField(verbose_name='Fecha y hora')
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='Estado',
    )
    notas_cliente = models.TextField(
        blank=True, verbose_name='Notas del cliente'
    )
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f'Cita #{self.pk} — {self.cliente} | {self.servicio} | {self.fecha_hora:%d/%m/%Y %H:%M}'
    
    @property
    def puede_confirmarse(self):
        return self.estado == self.Estado.PENDIENTE

    @property
    def puede_cancelarse(self):
        return self.estado in (self.Estado.PENDIENTE, self.Estado.CONFIRMADA)


class Pago(models.Model):
    """Registro del pago de una cita."""

    class MetodoPago(models.TextChoices):
        EFECTIVO = 'efectivo', 'Efectivo'
        TARJETA = 'tarjeta', 'Tarjeta'
        TRANSFERENCIA = 'transferencia', 'Transferencia'

    cita = models.OneToOneField(
        Cita,
        on_delete=models.PROTECT,
        related_name='pago',
        verbose_name='Cita',
    )
    monto = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Monto pagado'
    )
    metodo = models.CharField(
        max_length=15,
        choices=MetodoPago.choices,
        default=MetodoPago.EFECTIVO,
        verbose_name='Método de pago',
    )
    referencia = models.CharField(
        max_length=100, blank=True, verbose_name='Referencia / Folio'
    )
    pagado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f'Pago ${self.monto} — Cita #{self.cita_id}'
