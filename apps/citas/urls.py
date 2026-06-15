"""URLs del módulo de Citas."""
from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    # Vehículos
    path('vehiculos/', views.VehiculoListView.as_view(), name='vehiculos'),
    path('vehiculos/nuevo/', views.VehiculoCreateView.as_view(), name='crear_vehiculo'),
    path('vehiculos/<int:pk>/editar/', views.VehiculoUpdateView.as_view(), name='editar_vehiculo'),

    # Citas
    path('', views.CitaListView.as_view(), name='lista'),
    path('nueva/', views.CitaCreateView.as_view(), name='crear'),
    path('<int:pk>/editar/', views.CitaUpdateView.as_view(), name='editar'),
    path('<int:pk>/cancelar/', views.CitaCancelarView.as_view(), name='cancelar'),
    path('<int:pk>/confirmar/', views.CitaConfirmarView.as_view(), name='confirmar'),  # RF-05

    # Pagos
    path('pagos/nuevo/', views.PagoCreateView.as_view(), name='pago'),

    # Agenda
    path('agenda/', views.AgendaHoyView.as_view(), name='agenda'),  # RF-08
    
    # API
     path('api/horarios/', views.HorariosDisponiblesView.as_view(), name='api_horarios'),
     path('api/precio/', views.PrecioCitaView.as_view(), name='api_precio'),    
] 