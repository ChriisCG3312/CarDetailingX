"""URL y vista del dashboard principal (despacha por rol)."""
from django.urls import path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.servicios.models import Servicio

from apps.citas.models import Cita
from apps.usuarios.models import Usuario

app_name = 'dashboard'


@login_required
def home(request):
    """
    Dashboard principal.
    Cada dev puede expandir el contexto de su módulo aquí,
    o crear sub-dashboards en su propia app y redirigir desde aquí.
    """
    context = {
        "usuario": request.user,
        "total_usuarios": Usuario.objects.count(),
        "total_servicios": Servicio.objects.count(),

        "servicios_pendientes": Cita.objects.filter(estado='pendiente').count(),  # D2: Servicio.objects.filter(activo=True).count()
    }

    # D1: añadir stats de usuarios cuando el módulo esté listo
    # if request.user.es_admin:
    #     from apps.usuarios.models import Usuario
    #     context['total_usuarios'] = Usuario.objects.count()

    # D2: añadir stats de servicios
    # from apps.servicios.models import Servicio
    # context['total_servicios'] = Servicio.objects.filter(activo=True).count()

    # D3: añadir citas del día
    # from apps.citas.models import Cita
    # from django.utils import timezone
    # context['citas_hoy'] = Cita.objects.filter(fecha_hora__date=timezone.now().date())

    # D4: añadir notificaciones pendientes
    # from apps.seguimiento.models import Notificacion
    # context['notificaciones'] = Notificacion.objects.filter(
    #     usuario=request.user, leida=False
    # )

    return render(request, 'dashboard.html', context)


urlpatterns = [
    path('', home, name='home'),
]
