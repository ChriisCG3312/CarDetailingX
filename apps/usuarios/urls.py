"""URLs del módulo de usuarios."""
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('registro/', views.RegistroView.as_view(), name='registro'),

    # CRUD de usuarios (Admin)
    path('', views.UsuarioListView.as_view(), name='lista'),
    path('nuevo/', views.UsuarioCreateView.as_view(), name='crear'),
    path('<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.UsuarioDeleteView.as_view(), name='eliminar'),
    path('<int:pk>/reactivar/', views.UsuarioReactivateView.as_view(), name='reactivar'),
]
