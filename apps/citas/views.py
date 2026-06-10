"""
Vistas del módulo de Citas y Pagos.
Responsable: D3
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Cita, Vehiculo, Pago
from .forms import CitaForm, VehiculoForm, PagoForm
from apps.usuarios.mixins import AdminRequiredMixin, ClienteRequiredMixin


# ── Vehículos ─────────────────────────────────────────────────────────────────

class VehiculoListView(LoginRequiredMixin, ListView):
    model = Vehiculo
    template_name = 'citas/vehiculos_lista.html'
    context_object_name = 'vehiculos'

    def get_queryset(self):
        # Cliente solo ve sus propios vehículos; Admin los ve todos
        if self.request.user.es_admin:
            return Vehiculo.objects.select_related('cliente').all()
        return Vehiculo.objects.filter(cliente=self.request.user)


class VehiculoCreateView(LoginRequiredMixin, CreateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'citas/vehiculo_form.html'
    success_url = reverse_lazy('citas:vehiculos')

    def form_valid(self, form):
        form.instance.cliente = self.request.user
        messages.success(self.request, 'Vehículo registrado correctamente.')
        return super().form_valid(form)


class VehiculoUpdateView(LoginRequiredMixin, UpdateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'citas/vehiculo_form.html'
    success_url = reverse_lazy('citas:vehiculos')

    def get_queryset(self):
        if self.request.user.es_admin:
            return Vehiculo.objects.all()
        return Vehiculo.objects.filter(cliente=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Vehículo actualizado.')
        return super().form_valid(form)


# ── Citas ─────────────────────────────────────────────────────────────────────

class CitaListView(LoginRequiredMixin, ListView):
    model = Cita
    template_name = 'citas/lista.html'
    context_object_name = 'citas'
    paginate_by = 15

    def get_queryset(self):
        qs = Cita.objects.select_related('cliente', 'vehiculo', 'servicio')
        if self.request.user.es_admin:
            return qs
        return qs.filter(cliente=self.request.user)


class CitaCreateView(LoginRequiredMixin, CreateView):
    model = Cita
    form_class = CitaForm
    template_name = 'citas/form.html'
    success_url = reverse_lazy('citas:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.cliente = self.request.user
        messages.success(self.request, 'Cita agendada correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Agendar cita'
        return ctx


class CitaUpdateView(AdminRequiredMixin, UpdateView):
    """Solo el Admin puede editar una cita ya existente."""
    model = Cita
    form_class = CitaForm
    template_name = 'citas/form.html'
    success_url = reverse_lazy('citas:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Cita actualizada.')
        return super().form_valid(form)


class CitaCancelarView(LoginRequiredMixin, UpdateView):
    """Cliente o Admin pueden cancelar una cita pendiente."""
    model = Cita
    fields = []
    template_name = 'citas/confirmar_cancelar.html'
    success_url = reverse_lazy('citas:lista')

    def form_valid(self, form):
        cita = form.instance
        if cita.puede_cancelarse:
            cita.estado = Cita.Estado.CANCELADA
            cita.save()
            messages.success(self.request, 'Cita cancelada.')
        else:
            messages.error(self.request, 'Esta cita no se puede cancelar en su estado actual.')
        return super().form_valid(form)


# ── Pagos ─────────────────────────────────────────────────────────────────────

class PagoCreateView(AdminRequiredMixin, CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'citas/pago_form.html'
    success_url = reverse_lazy('citas:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Pago registrado.')
        return super().form_valid(form)
