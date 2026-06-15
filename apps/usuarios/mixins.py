"""
Mixins de permisos reutilizables en todas las apps.
Importar desde aquí en cualquier app que lo necesite.

Uso:
    from apps.usuarios.mixins import AdminRequiredMixin, TecnicoRequiredMixin
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect


class RolRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Base para mixins de rol. No usar directamente."""
    rol_requerido = None
    mensaje_denegado = 'No tienes permisos para acceder a esta sección.'

    def test_func(self):
        user = self.request.user
        if self.rol_requerido is None:
            return user.is_authenticated
        return user.rol == self.rol_requerido or user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        messages.error(self.request, self.mensaje_denegado)
        return redirect('dashboard:home')


class AdminRequiredMixin(RolRequiredMixin):
    """Solo accesible para usuarios con rol Administrador."""
    rol_requerido = 'admin'
    mensaje_denegado = 'Solo los administradores pueden acceder a esta sección.'


class TecnicoRequiredMixin(RolRequiredMixin):
    """Solo accesible para Técnicos (y Admins)."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.rol in ('tecnico', 'admin') or user.is_superuser
        )


class ClienteRequiredMixin(RolRequiredMixin):
    """Solo accesible para Clientes (y Admins)."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.rol in ('cliente', 'admin') or user.is_superuser
        )
