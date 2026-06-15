"""Utilidades compartidas del módulo de Reportes."""
from django.utils import timezone


def obtener_rango_fechas(request, dias_default=30):
    """
    Parsea fecha_inicio y fecha_fin desde GET.
    Por defecto: primer día del mes actual hasta hoy.
    Si se pasa dias_default, usa los últimos N días.
    """
    hoy = timezone.localdate()

    # fecha_inicio por defecto: primer día del mes actual
    inicio_default = hoy.replace(day=1)

    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    try:
        from datetime import date
        fecha_inicio = date.fromisoformat(fecha_inicio_str) if fecha_inicio_str else inicio_default
    except ValueError:
        fecha_inicio = inicio_default

    try:
        from datetime import date
        fecha_fin = date.fromisoformat(fecha_fin_str) if fecha_fin_str else hoy
    except ValueError:
        fecha_fin = hoy

    return fecha_inicio, fecha_fin


def formato_moneda(valor):
    """Formatea un número como moneda mexicana."""
    if valor is None:
        return '$0.00 MXN'
    return f'${valor:,.2f} MXN'


def formato_duracion(duracion):
    """Convierte un timedelta a formato Xh Ym."""
    if not duracion:
        return '—'
    total_segundos = int(duracion.total_seconds())
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    return f'{horas}h {minutos}m'