"""
Módulo: Seguimiento y Notificaciones
Responsable: D4

Modelos:
- Seguimiento: estado en tiempo real del servicio técnico de una cita.
- Notificacion: alertas internas enviadas a un usuario del sistema.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.citas.models import Cita


class Seguimiento(models.Model):

    class Estado(models.TextChoices):
        EN_ESPERA   = 'en_espera',   'En espera'
        RECIBIDO    = 'recibido',    'Vehículo recibido'
        EN_DETALLES = 'en_detalles', 'En detalles'
        LISTO       = 'listo',       'Listo para entrega'
        ENTREGADO   = 'entregado',   'Entregado al cliente'

    ORDEN_ESTADOS = [
        'en_espera', 'recibido', 'en_detalles', 'listo', 'entregado',
    ]

    cita = models.OneToOneField(
        Cita,
        on_delete=models.PROTECT,
        related_name='seguimiento',
        verbose_name='Cita',
    )
    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='seguimientos',
        verbose_name='Técnico asignado',
        limit_choices_to={'rol': 'tecnico'},
    )
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.EN_ESPERA,
        verbose_name='Estado',
    )
    notas_iniciales = models.TextField(blank=True, verbose_name='Notas iniciales')
    notas_tecnico   = models.TextField(blank=True, verbose_name='Notas del técnico')
    foto_antes = models.ImageField(
        upload_to='seguimiento/antes/',
        blank=True, null=True,
        verbose_name='Foto antes del servicio',
    )
    foto_despues = models.ImageField(
        upload_to='seguimiento/despues/',
        blank=True, null=True,
        verbose_name='Foto después del servicio',
    )
    creado_en      = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Seguimiento'
        verbose_name_plural = 'Seguimientos'
        ordering = ['-actualizado_en']

    def __str__(self):
        return f'Seguimiento #{self.pk} — {self.cita} [{self.get_estado_display()}]'

    def estado_index(self):
        return self.ORDEN_ESTADOS.index(self.estado)

    def puede_avanzar_a(self, nuevo_estado):
        try:
            return self.ORDEN_ESTADOS.index(nuevo_estado) > self.estado_index()
        except ValueError:
            return False

    @property
    def cita_disponible(self):
        """True si ya llegó la fecha y hora de la cita."""
        return timezone.now() >= self.cita.fecha_hora


class Notificacion(models.Model):

    class Tipo(models.TextChoices):
        CITA_CONFIRMADA   = 'cita_confirmada',   'Cita confirmada'
        CITA_CANCELADA    = 'cita_cancelada',    'Cita cancelada'
        SERVICIO_INICIADO = 'servicio_iniciado', 'Servicio iniciado'
        SERVICIO_LISTO    = 'servicio_listo',    'Servicio listo'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name='Usuario',
    )
    cita = models.ForeignKey(
        Cita,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notificaciones',
        verbose_name='Cita relacionada',
    )
    tipo    = models.CharField(max_length=20, choices=Tipo.choices, verbose_name='Tipo')
    mensaje = models.TextField(verbose_name='Mensaje')
    leida   = models.BooleanField(default=False, verbose_name='Leída')
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-creada_en']

    def __str__(self):
        estado = 'leída' if self.leida else 'no leída'
        return f'Notif [{self.tipo}] → {self.usuario} ({estado})'