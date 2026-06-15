"""
Señales de Django para generar notificaciones automáticas.
Responsable: D4

Registrar en apps/seguimiento/apps.py → ready()
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='citas.Cita')
def notificar_cambio_estado_cita(sender, instance, created, **kwargs):
    """
    Cuando una Cita cambia de estado, crea una Notificacion para el cliente.
    """
    from .models import Notificacion

    if created:
        Notificacion.objects.create(
            usuario=instance.cliente,
            tipo=Notificacion.Tipo.CITA_CONFIRMADA,
            titulo='Cita registrada',
            mensaje=f'Tu cita para {instance.servicio} el {instance.fecha_hora:%d/%m/%Y a las %H:%M} ha sido registrada.',
            cita=instance,
        )
    elif instance.estado == 'cancelada':
        Notificacion.objects.create(
            usuario=instance.cliente,
            tipo=Notificacion.Tipo.CITA_CANCELADA,
            titulo='Cita cancelada',
            mensaje=f'Tu cita del {instance.fecha_hora:%d/%m/%Y} ha sido cancelada.',
            cita=instance,
        )


@receiver(post_save, sender='seguimiento.Seguimiento')
def notificar_cambio_seguimiento(sender, instance, created, **kwargs):
    """
    Cuando el técnico actualiza el seguimiento, notifica al cliente.
    """
    from .models import Notificacion

    if instance.estado_actual == 'listo':
        Notificacion.objects.create(
            usuario=instance.cita.cliente,
            tipo=Notificacion.Tipo.SERVICIO_LISTO,
            titulo='¡Tu vehículo está listo!',
            mensaje=f'El servicio de {instance.cita.servicio} ha finalizado. Puedes pasar a recogerlo.',
            cita=instance.cita,
        )
    elif not created:
        Notificacion.objects.create(
            usuario=instance.cita.cliente,
            tipo=Notificacion.Tipo.SERVICIO_INICIADO,
            titulo='Actualización de tu servicio',
            mensaje=f'Estado actual: {instance.get_estado_actual_display()}. {instance.notas}',
            cita=instance.cita,
        )
