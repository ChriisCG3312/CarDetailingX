"""
Módulo: Seguimiento y Notificaciones
Responsable: D4

Modelos:
- Seguimiento: estado en tiempo real del servicio técnico de una cita.
- Notificacion: alertas internas enviadas a un usuario del sistema.
"""
from django.db import models
from django.conf import settings
from apps.citas.models import Cita


class Seguimiento(models.Model):
    """Estado del servicio técnico asignado a una cita."""

    class EstadoServicio(models.TextChoices):
        RECIBIDO = 'recibido', 'Vehículo recibido'
        EN_LAVADO = 'en_lavado', 'En lavado'
        EN_PULIDO = 'en_pulido', 'En pulido/encerado'
        EN_DETALLES = 'en_detalles', 'En detalles finales'
        LISTO = 'listo', 'Listo para entrega'
        ENTREGADO = 'entregado', 'Entregado al cliente'

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
    estado_actual = models.CharField(
        max_length=20,
        choices=EstadoServicio.choices,
        default=EstadoServicio.RECIBIDO,
        verbose_name='Estado del servicio',
    )
    notas = models.TextField(blank=True, verbose_name='Notas del técnico')
    foto_antes = models.ImageField(
        upload_to='seguimiento/antes/', blank=True, null=True,
        verbose_name='Foto antes'
    )
    foto_despues = models.ImageField(
        upload_to='seguimiento/despues/', blank=True, null=True,
        verbose_name='Foto después'
    )
    iniciado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Seguimiento'
        verbose_name_plural = 'Seguimientos'
        ordering = ['-actualizado_en']

    def __str__(self):
        return f'Seguimiento Cita #{self.cita_id} — {self.get_estado_actual_display()}'


class Notificacion(models.Model):
    """Notificación interna enviada a un usuario."""

    class Tipo(models.TextChoices):
        CITA_CONFIRMADA = 'cita_confirmada', 'Cita confirmada'
        CITA_CANCELADA = 'cita_cancelada', 'Cita cancelada'
        SERVICIO_INICIADO = 'servicio_iniciado', 'Servicio iniciado'
        SERVICIO_LISTO = 'servicio_listo', 'Vehículo listo'
        RECORDATORIO = 'recordatorio', 'Recordatorio de cita'
        GENERAL = 'general', 'Notificación general'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name='Destinatario',
    )
    tipo = models.CharField(
        max_length=25,
        choices=Tipo.choices,
        default=Tipo.GENERAL,
        verbose_name='Tipo',
    )
    titulo = models.CharField(max_length=100, verbose_name='Título')
    mensaje = models.TextField(verbose_name='Mensaje')
    leida = models.BooleanField(default=False, verbose_name='Leída')
    cita = models.ForeignKey(
        Cita,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notificaciones',
        verbose_name='Cita relacionada',
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-creada_en']

    def __str__(self):
        return f'[{"✓" if self.leida else "•"}] {self.titulo} → {self.usuario}'
