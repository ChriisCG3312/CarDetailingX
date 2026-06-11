def notificaciones_no_leidas(request):
    if request.user.is_authenticated:
        return {
            'notif_count': request.user.notificaciones.filter(leida=False).count()
        }
    return {'notif_count': 0}