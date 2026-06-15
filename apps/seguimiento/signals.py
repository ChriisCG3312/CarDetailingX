"""
Señales de Django para generar notificaciones automáticas.
Responsable: D4

Registrar en apps/seguimiento/apps.py → ready()
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.citas.models import Cita
from .models import Seguimiento, Notificacion


# ── Señales de Cita ─────────────────────────────────────────────────────────

@receiver(post_save, sender=Cita)
def notificar_cambio_cita(sender, instance, created, **kwargs):
    """Notifica al cliente cuando se crea o confirma/cancela una cita."""
    try:
        servicio = instance.servicio.nombre
        fecha    = instance.fecha_hora.strftime('%d/%m/%Y %H:%M')

        if created:
            Notificacion.objects.create(
                usuario=instance.cliente,
                cita=instance,
                tipo=Notificacion.Tipo.CITA_CONFIRMADA,
                mensaje=f'Tu cita para {servicio} el {fecha} ha sido registrada.',
            )
        else:
            if instance.estado == Cita.Estado.CONFIRMADA:
                Notificacion.objects.create(
                    usuario=instance.cliente,
                    cita=instance,
                    tipo=Notificacion.Tipo.CITA_CONFIRMADA,
                    mensaje=f'Tu cita del {fecha} ha sido confirmada.',
                )
            elif instance.estado == Cita.Estado.CANCELADA:
                Notificacion.objects.create(
                    usuario=instance.cliente,
                    cita=instance,
                    tipo=Notificacion.Tipo.CITA_CANCELADA,
                    mensaje=f'Tu cita del {fecha} ha sido cancelada.',
                )
    except Exception as e:
        # No interrumpir el flujo principal
        import logging
        logging.getLogger(__name__).error(f'Signal notificar_cambio_cita falló: {e}')


# ── Señales de Seguimiento ───────────────────────────────────────────────────

@receiver(post_save, sender=Seguimiento)
def notificar_cambio_seguimiento(sender, instance, created, **kwargs):
    """Notifica al cliente según el estado del seguimiento."""
    try:
        cliente = instance.cita.cliente
        fecha   = instance.cita.fecha_hora.strftime('%d/%m/%Y %H:%M')

        if created:
            # Vehículo recibido en taller
            Notificacion.objects.create(
                usuario=cliente,
                cita=instance.cita,
                tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                mensaje='Tu vehículo ha sido recibido en taller.',
            )
        else:
            if instance.estado == Seguimiento.Estado.LISTO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_LISTO,
                    mensaje='¡Tu vehículo está listo! Puedes pasar a recogerlo.',
                )
            elif instance.estado != Seguimiento.Estado.RECIBIDO:
                notas = f' {instance.notas_tecnico}' if instance.notas_tecnico else ''
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Estado actual: {instance.get_estado_display()}.{notas}',
                )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'Signal notificar_cambio_seguimiento falló: {e}')


@receiver(post_save, sender=Seguimiento)
def actualizar_estado_cita(sender, instance, **kwargs):
    """Sincroniza el estado de la Cita con el del Seguimiento."""
    try:
        cita = instance.cita
        if instance.estado == Seguimiento.Estado.ENTREGADO:
            if cita.estado != Cita.Estado.TERMINADA:
                # Usamos update() para no disparar post_save de Cita en bucle
                Cita.objects.filter(pk=cita.pk).update(estado=Cita.Estado.TERMINADA)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'Signal actualizar_estado_cita falló: {e}')