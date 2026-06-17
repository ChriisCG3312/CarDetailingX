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
        paquete = instance.paquete.nombre if instance.paquete else 'servicio'
        fecha   = instance.fecha_hora.strftime('%d/%m/%Y %H:%M')

        if created:
            Notificacion.objects.create(
                usuario=instance.cliente,
                cita=instance,
                tipo=Notificacion.Tipo.CITA_CONFIRMADA,
                mensaje=f'Tu cita para {paquete} el {fecha} ha sido registrada. '
                        f'En espera de confirmación.',
            )
        else:
            if instance.estado == Cita.Estado.CONFIRMADA:
                Notificacion.objects.create(
                    usuario=instance.cliente,
                    cita=instance,
                    tipo=Notificacion.Tipo.CITA_CONFIRMADA,
                    mensaje=f'Tu cita del {fecha} para {paquete} ha sido confirmada. '
                            f'Te esperamos.',
                )
            elif instance.estado == Cita.Estado.CANCELADA:
                Notificacion.objects.create(
                    usuario=instance.cliente,
                    cita=instance,
                    tipo=Notificacion.Tipo.CITA_CANCELADA,
                    mensaje=f'Tu cita del {fecha} para {paquete} ha sido cancelada. '
                            f'Contáctanos para más información.',
                )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'Signal notificar_cambio_cita falló: {e}')


# ── Señales de Seguimiento ───────────────────────────────────────────────────

@receiver(post_save, sender=Seguimiento)
def notificar_cambio_seguimiento(sender, instance, created, **kwargs):
    """Notifica al técnico al asignarse, y al cliente solo cuando el técnico actualiza estados."""
    try:
        cliente  = instance.cita.cliente
        tecnico  = instance.tecnico
        vehiculo = instance.cita.vehiculo
        paquete  = instance.cita.paquete.nombre if instance.cita.paquete else 'servicio'
        fecha    = instance.cita.fecha_hora.strftime('%d/%m/%Y %H:%M')

        if created:
            # Solo notificar al TÉCNICO — la cita puede ser para otro día
            Notificacion.objects.create(
                usuario=tecnico,
                cita=instance.cita,
                tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                mensaje=f'Se te ha asignado el vehículo {vehiculo} '
                        f'del cliente {cliente.get_full_name() or cliente.username}. '
                        f'Paquete: {paquete}. '
                        f'Fecha programada: {fecha}.',
            )
        else:
            if instance.estado == Seguimiento.Estado.RECIBIDO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Tu vehículo {vehiculo} ha sido recibido en taller '
                            f'y el servicio está por comenzar.',
                )
            elif instance.estado == Seguimiento.Estado.EN_LAVADO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Tu vehículo {vehiculo} está en proceso de lavado.',
                )
            elif instance.estado == Seguimiento.Estado.EN_PULIDO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Tu vehículo {vehiculo} está en proceso de pulido y encerado.',
                )
            elif instance.estado == Seguimiento.Estado.EN_DETALLES:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Tu vehículo {vehiculo} está en los detalles finales. '
                            f'¡Casi listo!',
                )
            elif instance.estado == Seguimiento.Estado.LISTO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_LISTO,
                    mensaje=f'¡Tu vehículo {vehiculo} está listo! '
                            f'Puedes pasar a recogerlo cuando gustes.',
                )
            elif instance.estado == Seguimiento.Estado.ENTREGADO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Tu vehículo {vehiculo} ha sido entregado. '
                            f'¡Gracias por tu preferencia!',
                )

    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'Signal notificar_cambio_seguimiento falló: {e}')


@receiver(post_save, sender=Seguimiento)
def actualizar_estado_cita(sender, instance, **kwargs):
    """Sincroniza el estado de la Cita con el del Seguimiento al entregar."""
    try:
        cita = instance.cita
        if instance.estado == Seguimiento.Estado.ENTREGADO:
            if cita.estado != Cita.Estado.TERMINADA:
                Cita.objects.filter(pk=cita.pk).update(estado=Cita.Estado.TERMINADA)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'Signal actualizar_estado_cita falló: {e}')