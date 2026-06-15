"""URL y vista del dashboard principal (despacha por rol)."""
from django.urls import path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.servicios.models import Servicio

from apps.citas.models import Cita
from apps.usuarios.models import Usuario
from apps.seguimiento.models import Seguimiento

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

        "servicios_pendientes": Cita.objects.filter(estado='pendiente').count(),  
        "servicios_activos": Seguimiento.objects.exclude(estado=Seguimiento.Estado.ENTREGADO).count(),
    }

    return render(request, 'dashboard.html', context)


urlpatterns = [
    path('', home, name='home'),
]
