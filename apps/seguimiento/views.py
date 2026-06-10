"""
Vistas del módulo de Seguimiento y Notificaciones.
Responsable: D4
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View
from django.shortcuts import get_object_or_404, redirect

from .models import Seguimiento, Notificacion
from .forms import SeguimientoForm
from apps.usuarios.mixins import AdminRequiredMixin, TecnicoRequiredMixin


# ── Seguimiento ───────────────────────────────────────────────────────────────

class SeguimientoListView(TecnicoRequiredMixin, ListView):
    """Lista de seguimientos activos para el técnico o admin."""
    model = Seguimiento
    template_name = 'seguimiento/lista.html'
    context_object_name = 'seguimientos'

    def get_queryset(self):
        qs = Seguimiento.objects.select_related('cita__cliente', 'cita__servicio', 'tecnico')
        if self.request.user.es_admin:
            return qs
        return qs.filter(tecnico=self.request.user)


class SeguimientoCreateView(AdminRequiredMixin, CreateView):
    """El Admin asigna un técnico y crea el seguimiento para una cita."""
    model = Seguimiento
    form_class = SeguimientoForm
    template_name = 'seguimiento/form.html'
    success_url = reverse_lazy('seguimiento:lista')

    def form_valid(self, form):
        # Cambiar estado de la cita a "en proceso"
        seguimiento = form.save(commit=False)
        cita = seguimiento.cita
        cita.estado = 'en_proceso'
        cita.save()
        messages.success(self.request, 'Seguimiento iniciado.')
        return super().form_valid(form)


class SeguimientoUpdateView(TecnicoRequiredMixin, UpdateView):
    """Técnico actualiza el estado del servicio."""
    model = Seguimiento
    form_class = SeguimientoForm
    template_name = 'seguimiento/form.html'
    success_url = reverse_lazy('seguimiento:lista')

    def get_queryset(self):
        if self.request.user.es_admin:
            return Seguimiento.objects.all()
        return Seguimiento.objects.filter(tecnico=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Seguimiento actualizado.')
        return super().form_valid(form)


# ── Notificaciones ────────────────────────────────────────────────────────────

class NotificacionListView(LoginRequiredMixin, ListView):
    """Bandeja de notificaciones del usuario actual."""
    model = Notificacion
    template_name = 'seguimiento/notificaciones.html'
    context_object_name = 'notificaciones'
    paginate_by = 20

    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user)


class MarcarLeidaView(LoginRequiredMixin, View):
    """Marca una notificación como leída vía POST."""
    def post(self, request, pk):
        notif = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
        notif.leida = True
        notif.save(update_fields=['leida'])
        return redirect('seguimiento:notificaciones')


class MarcarTodasLeidasView(LoginRequiredMixin, View):
    """Marca todas las notificaciones del usuario como leídas."""
    def post(self, request):
        Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
        messages.success(request, 'Todas las notificaciones marcadas como leídas.')
        return redirect('seguimiento:notificaciones')
