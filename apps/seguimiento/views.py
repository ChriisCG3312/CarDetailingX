"""
Vistas del módulo de Seguimiento y Notificaciones.
Responsable: D4
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView, View
from django.http import JsonResponse
from apps.citas.models import Cita
from .models import Seguimiento, Notificacion
from .forms import SeguimientoCrearForm, SeguimientoActualizarForm


# ── Mixins de rol ────────────────────────────────────────────────────────────

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.es_admin


class TecnicoRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.es_tecnico or self.request.user.es_admin


# ── RF-01 Crear seguimiento (Admin) ─────────────────────────────────────────

class SeguimientoCrearView(AdminRequiredMixin, CreateView):
    model = Seguimiento
    form_class = SeguimientoCrearForm
    template_name = 'seguimiento/seguimiento_form.html'
    success_url = reverse_lazy('seguimiento:lista')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        cita_pk = self.request.GET.get('cita')
        if cita_pk:
            try:
                form.fields['cita'].initial = int(cita_pk)
            except (ValueError, TypeError):
                pass
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cita_pk = self.request.GET.get('cita')
        if cita_pk:
            try:
                cita = Cita.objects.select_related('cliente', 'paquete', 'vehiculo').get(pk=cita_pk)
                ctx['cita_preseleccionada'] = str(cita)
                ctx['cita_pk'] = cita.pk
            except Cita.DoesNotExist:
                pass
        return ctx

    def form_valid(self, form):
        seguimiento = form.save()
        cita = seguimiento.cita
        cita.estado = Cita.Estado.EN_PROCESO
        cita.save()
        messages.success(self.request, f'Seguimiento creado. Técnico asignado: {seguimiento.tecnico}.')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Corrige los errores del formulario.')
        return super().form_invalid(form)


# ── RF-02 Actualizar estado (Técnico / Admin) ────────────────────────────────

class SeguimientoActualizarView(TecnicoRequiredMixin, UpdateView):
    model = Seguimiento
    form_class = SeguimientoActualizarForm
    template_name = 'seguimiento/seguimiento_actualizar.html'
    success_url = reverse_lazy('seguimiento:lista')

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            Seguimiento.objects.select_related('cita__cliente', 'cita__paquete', 'tecnico'),
            pk=self.kwargs['pk'],
        )
        if self.request.user.es_tecnico and obj.tecnico != self.request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return obj

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.estado == Seguimiento.Estado.ENTREGADO:
            messages.error(request, 'Este servicio ya fue entregado al cliente y no puede modificarse.')
            return redirect('seguimiento:lista')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.estado == Seguimiento.Estado.ENTREGADO:
            messages.error(request, 'Este servicio ya fue entregado al cliente y no puede modificarse.')
            return redirect('seguimiento:lista')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Estado actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Corrige los errores del formulario.')
        return super().form_invalid(form)


# ── RF-03 Lista de seguimientos activos ──────────────────────────────────────

class SeguimientoListaView(LoginRequiredMixin, ListView):
    model = Seguimiento
    template_name = 'seguimiento/seguimiento_lista.html'
    context_object_name = 'seguimientos'
    paginate_by = 20

    def get_queryset(self):
        qs = Seguimiento.objects.select_related(
            'cita__cliente', 'cita__paquete', 'cita__vehiculo', 'tecnico'
        )
        if not self.request.GET.get('ver_entregados'):
            qs = qs.exclude(estado=Seguimiento.Estado.ENTREGADO)

        if self.request.user.es_tecnico:
            qs = qs.filter(tecnico=self.request.user)

        return qs.order_by('-actualizado_en')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['ver_entregados'] = self.request.GET.get('ver_entregados', False)
        return ctx


# ── RF-04 Detalle (Cliente — solo lectura) ───────────────────────────────────

class SeguimientoDetalleClienteView(LoginRequiredMixin, DetailView):
    model = Seguimiento
    template_name = 'seguimiento/seguimiento_detalle_cliente.html'
    context_object_name = 'seguimiento'

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            Seguimiento.objects.select_related('cita__cliente', 'cita__paquete', 'tecnico'),
            pk=self.kwargs['pk'],
        )
        if self.request.user.es_cliente and obj.cita.cliente != self.request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return obj


# ── RF-06 Bandeja de notificaciones ─────────────────────────────────────────

class NotificacionListaView(LoginRequiredMixin, ListView):
    model = Notificacion
    template_name = 'seguimiento/notificaciones.html'
    context_object_name = 'notificaciones'
    paginate_by = 20

    def get_queryset(self):
        return Notificacion.objects.filter(
            usuario=self.request.user
        ).select_related('cita').order_by('-creada_en')


class MarcarTodasLeidasView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        Notificacion.objects.filter(
            usuario=request.user, leida=False
        ).update(leida=True)
        messages.success(request, 'Todas las notificaciones marcadas como leídas.')
        return redirect('seguimiento:notificaciones')


class MarcarLeidaView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        notif = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
        notif.leida = True
        notif.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
        return redirect('seguimiento:notificaciones')