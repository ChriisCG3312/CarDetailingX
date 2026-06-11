"""
Vistas del módulo de Citas y Pagos.
Responsable: D3
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, TemplateView

from .models import Cita, Vehiculo, Pago
from .forms import CitaForm, VehiculoForm, PagoForm
from apps.usuarios.mixins import AdminRequiredMixin, ClienteRequiredMixin


# ── Vehículos ─────────────────────────────────────────────────────────────────

class VehiculoListView(LoginRequiredMixin, ListView):
    model = Vehiculo
    template_name = 'citas/vehiculos_lista.html'
    context_object_name = 'vehiculos'

    def get_queryset(self):
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

    def dispatch(self, request, *args, **kwargs):
        # RF-04: técnico no accede a esta vista
        if request.user.is_authenticated and request.user.rol == 'tecnico':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = Cita.objects.select_related('cliente', 'vehiculo', 'servicio')
        if not self.request.user.es_admin:
            qs = qs.filter(cliente=self.request.user)

        # RF-04: filtro por estado desde ?estado=
        estado = self.request.GET.get('estado')
        if estado in Cita.Estado.values:
            qs = qs.filter(estado=estado)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['estados'] = Cita.Estado.choices
        ctx['estado_activo'] = self.request.GET.get('estado', '')
        return ctx


class CitaCreateView(LoginRequiredMixin, CreateView):
    model = Cita
    form_class = CitaForm
    template_name = 'citas/form.html'
    success_url = reverse_lazy('citas:lista')

    def dispatch(self, request, *args, **kwargs):
        # RF-03: sin vehículos → redirigir con mensaje informativo
        if (
            request.user.is_authenticated
            and not request.user.es_admin
            and not Vehiculo.objects.filter(cliente=request.user).exists()
        ):
            messages.info(request, 'Primero registra un vehículo para poder agendar una cita.')
            return redirect('citas:crear_vehiculo')
        return super().dispatch(request, *args, **kwargs)

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


class CitaConfirmarView(AdminRequiredMixin, UpdateView):
    """RF-05: Admin confirma una cita pendiente."""
    model = Cita
    fields = []
    template_name = 'citas/confirmar_accion.html'
    success_url = reverse_lazy('citas:lista')

    def form_valid(self, form):
        cita = form.instance
        if cita.estado == Cita.Estado.CANCELADA:
            messages.error(self.request, 'No se puede confirmar una cita cancelada.')
            return redirect(self.success_url)
        if not cita.puede_confirmarse:
            messages.error(self.request, 'Esta cita no puede confirmarse en su estado actual.')
            return redirect(self.success_url)
        cita.estado = Cita.Estado.CONFIRMADA
        cita.save()
        messages.success(self.request, f'Cita #{cita.pk} confirmada.')
        return redirect(self.success_url)


class CitaCancelarView(LoginRequiredMixin, UpdateView):
    """RF-06: Cliente o Admin cancelan una cita pendiente o confirmada."""
    model = Cita
    fields = []
    template_name = 'citas/confirmar_cancelar.html'
    success_url = reverse_lazy('citas:lista')

    def get_queryset(self):
        # RF-06: cliente solo puede cancelar sus propias citas
        if self.request.user.es_admin:
            return Cita.objects.all()
        return Cita.objects.filter(cliente=self.request.user)

    def form_valid(self, form):
        cita = form.instance

        # RF-06: mensajes de error específicos por estado
        if cita.estado == Cita.Estado.EN_PROCESO:
            messages.error(self.request, 'No puedes cancelar una cita que ya está en proceso.')
            return redirect(self.success_url)
        if cita.estado == Cita.Estado.TERMINADA:
            messages.error(self.request, 'No puedes cancelar una cita ya terminada.')
            return redirect(self.success_url)

        if cita.puede_cancelarse:
            cita.estado = Cita.Estado.CANCELADA
            cita.save()
            messages.success(self.request, 'Cita cancelada.')
        else:
            messages.error(self.request, 'Esta cita no se puede cancelar en su estado actual.')

        return redirect(self.success_url)


# ── Pagos ─────────────────────────────────────────────────────────────────────

class PagoCreateView(AdminRequiredMixin, CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'citas/pago_form.html'
    success_url = reverse_lazy('citas:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Pago registrado.')
        return super().form_valid(form)


# ── Agenda del día ────────────────────────────────────────────────────────────

class AgendaHoyView(AdminRequiredMixin, TemplateView):
    """RF-08: Vista del admin con todas las citas del día."""
    template_name = 'citas/agenda_hoy.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = timezone.localdate()
        ctx['citas_hoy'] = (
            Cita.objects
            .filter(fecha_hora__date=hoy)
            .exclude(estado=Cita.Estado.CANCELADA)
            .select_related('cliente', 'vehiculo', 'servicio')
            .order_by('fecha_hora')
        )
        ctx['hoy'] = hoy
        return ctx
