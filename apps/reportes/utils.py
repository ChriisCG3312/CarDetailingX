from datetime import timedelta
from django.utils import timezone


def obtener_rango_fechas(request, dias_default=None):
    """
    Parsea fecha_inicio y fecha_fin desde GET.

    Si dias_default tiene valor, usa los últimos N días.
    En caso contrario usa el primer día del mes actual hasta hoy.
    """
    hoy = timezone.localdate()

    if dias_default:
        inicio_default = hoy - timedelta(days=dias_default)
    else:
        inicio_default = hoy.replace(day=1)

    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    try:
        from datetime import date
        fecha_inicio = (
            date.fromisoformat(fecha_inicio_str)
            if fecha_inicio_str else inicio_default
        )
    except ValueError:
        fecha_inicio = inicio_default

    try:
        from datetime import date
        fecha_fin = (
            date.fromisoformat(fecha_fin_str)
            if fecha_fin_str else hoy
        )
    except ValueError:
        fecha_fin = hoy

    return fecha_inicio, fecha_fin