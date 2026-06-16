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
                mensaje=f'Tu cita para {servicio} el {fecha} ha sido registrada. '
                        f'En espera de confirmación.',
            )
        else:
            if instance.estado == Cita.Estado.CONFIRMADA:
                Notificacion.objects.create(
                    usuario=instance.cliente,
                    cita=instance,
                    tipo=Notificacion.Tipo.CITA_CONFIRMADA,
                    mensaje=f'Tu cita del {fecha} para {servicio} ha sido confirmada. '
                            f'Te esperamos.',
                )
            elif instance.estado == Cita.Estado.CANCELADA:
                Notificacion.objects.create(
                    usuario=instance.cliente,
                    cita=instance,
                    tipo=Notificacion.Tipo.CITA_CANCELADA,
                    mensaje=f'Tu cita del {fecha} para {servicio} ha sido cancelada. '
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
        cliente = instance.cita.cliente
        tecnico = instance.tecnico
        fecha   = instance.cita.fecha_hora.strftime('%d/%m/%Y %H:%M')

        if created:
            # Solo notificar al TÉCNICO — la cita puede ser para otro día
            Notificacion.objects.create(
                usuario=tecnico,
                cita=instance.cita,
                tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                mensaje=f'Se te ha asignado el vehículo {instance.cita.vehiculo} '
                        f'del cliente {cliente.get_full_name() or cliente.username}. '
                        f'Servicio: {instance.cita.servicio}. '
                        f'Fecha programada: {fecha}.',
            )
            # NO notificar al cliente todavía — el servicio aún no ha comenzado

        else:
            # El técnico actualiza el estado — ahora sí notificar al cliente
            if instance.estado == Seguimiento.Estado.RECIBIDO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje='Tu vehículo ha sido recibido en taller y el servicio '
                            'está por comenzar.',
                )
            elif instance.estado == Seguimiento.Estado.EN_LAVADO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Tu vehículo {instance.cita.vehiculo} está en proceso '
                            f'de lavado.',
                )
            elif instance.estado == Seguimiento.Estado.EN_PULIDO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Tu vehículo {instance.cita.vehiculo} está en proceso '
                            f'de pulido y encerado.',
                )
            elif instance.estado == Seguimiento.Estado.EN_DETALLES:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Tu vehículo {instance.cita.vehiculo} está en los '
                            f'detalles finales. ¡Casi listo!',
                )
            elif instance.estado == Seguimiento.Estado.LISTO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_LISTO,
                    mensaje=f'¡Tu vehículo {instance.cita.vehiculo} está listo! '
                            f'Puedes pasar a recogerlo cuando gustes.',
                )
            elif instance.estado == Seguimiento.Estado.ENTREGADO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Tu vehículo {instance.cita.vehiculo} ha sido entregado. '
                            f'¡Gracias por tu preferencia!',
                )
<<<<<<< HEAD
=======
            elif instance.estado == Seguimiento.Estado.EN_LAVADO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Tu vehículo {instance.cita.vehiculo} está en proceso '
                            f'de lavado.',
                )
            elif instance.estado == Seguimiento.Estado.EN_PULIDO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Tu vehículo {instance.cita.vehiculo} está en proceso '
                            f'de pulido y encerado.',
                )
            elif instance.estado == Seguimiento.Estado.EN_DETALLES:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Tu vehículo {instance.cita.vehiculo} está en los '
                            f'detalles finales. ¡Casi listo!',
                )
            elif instance.estado == Seguimiento.Estado.LISTO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_LISTO,
                    mensaje=f'¡Tu vehículo {instance.cita.vehiculo} está listo! '
                            f'Puedes pasar a recogerlo cuando gustes.',
                )
            elif instance.estado == Seguimiento.Estado.ENTREGADO:
                Notificacion.objects.create(
                    usuario=cliente,
                    cita=instance.cita,
                    tipo=Notificacion.Tipo.SERVICIO_INICIADO,
                    mensaje=f'Tu vehículo {instance.cita.vehiculo} ha sido entregado. '
                            f'¡Gracias por tu preferencia!',
                )
>>>>>>> 6610610 (fix???)

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
                # Usamos update() para no disparar post_save de Cita en bucle
                Cita.objects.filter(pk=cita.pk).update(estado=Cita.Estado.TERMINADA)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'Signal actualizar_estado_cita falló: {e}')