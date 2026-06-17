"""
Vistas del módulo de Citas y Pagos.
Responsable: D3
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, TemplateView, View
from datetime import date as date_type

from .models import Cita, Vehiculo, Pago
from .forms import CitaForm, VehiculoForm, PagoForm
from apps.usuarios.mixins import AdminRequiredMixin, ClienteRequiredMixin

from django.views.generic import CreateView
from datetime import date

# Asegúrate de importar tus modelos y formularios correspondientes
from apps.citas.models import Cita
from apps.citas.forms import CitaForm  # O como se llame tu formulario de citas
from apps.servicios.forms import PaquetePersonalizadoForm

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages

from apps.servicios.models import Servicio  # Importamos el modelo de Servicio para calcular costos


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
        if request.user.is_authenticated and request.user.rol == 'tecnico':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = Cita.objects.select_related('cliente', 'vehiculo', 'paquete')
        if not self.request.user.es_admin:
            qs = qs.filter(cliente=self.request.user)

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
        if request.user.is_authenticated and not request.user.es_admin:
            if not Vehiculo.objects.filter(cliente=request.user).exists():
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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        paquete_pk = self.request.GET.get('paquete')
        if paquete_pk:
            try:
                form.fields['paquete'].initial = int(paquete_pk)
            except (ValueError, TypeError):
                pass
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Agendar cita'
        ctx['hoy'] = timezone.localdate()
        paquete_pk = self.request.GET.get('paquete')
        if paquete_pk:
            from apps.servicios.models import Paquete
            try:
                paquete = Paquete.objects.get(pk=paquete_pk)
                ctx['paquete_preseleccionado'] = paquete.nombre
                ctx['paquete_pk'] = paquete.pk
            except Paquete.DoesNotExist:
                pass
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
        from django.urls import reverse
        return redirect(reverse('seguimiento:crear') + f'?cita={cita.pk}')


class CitaCancelarView(LoginRequiredMixin, UpdateView):
    """RF-06: Cliente o Admin cancelan una cita pendiente o confirmada."""
    model = Cita
    fields = []
    template_name = 'citas/confirmar_cancelar.html'
    success_url = reverse_lazy('citas:lista')

    def get_queryset(self):
        if self.request.user.es_admin:
            return Cita.objects.all()
        return Cita.objects.filter(cliente=self.request.user)

    def form_valid(self, form):
        cita = form.instance

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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        siguiente = Pago.objects.count() + 1
        ctx['folio_preview'] = f'FOLIO-{siguiente:04d}'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.referencia = f'FOLIO-{self.object.pk:04d}'
        self.object.save()
        messages.success(self.request, f'Pago registrado. Folio: {self.object.referencia}')
        return response


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
            .select_related('cliente', 'vehiculo', 'paquete')
            .order_by('fecha_hora')
        )
        ctx['hoy'] = hoy
        return ctx


# ── API: horarios disponibles por día ─────────────────────────────────────────

class HorariosDisponiblesView(LoginRequiredMixin, View):
    """
    GET /citas/api/horarios/?fecha=2026-06-15
    Devuelve los slots del día con su disponibilidad.
    """
    http_method_names = ['get']
    SLOTS = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

    def get(self, request):
        fecha_str = request.GET.get('fecha')
        if not fecha_str:
            return JsonResponse({'error': 'Falta el parámetro fecha'}, status=400)

        try:
            fecha = date_type.fromisoformat(fecha_str)
        except ValueError:
            return JsonResponse({'error': 'Fecha inválida'}, status=400)

        hoy = timezone.localdate()
        if fecha < hoy or fecha.weekday() == 6:
            return JsonResponse({'slots': []})

        citas_del_dia = (
            Cita.objects
            .filter(fecha_hora__date=fecha)
            .exclude(estado=Cita.Estado.CANCELADA)
            .values_list('fecha_hora', flat=True)
        )

        horas_ocupadas = set()
        for dt in citas_del_dia:
            hora_local = timezone.localtime(dt).hour
            horas_ocupadas.add(hora_local)

        ahora = timezone.localtime(timezone.now())
        slots = []
        for hora in self.SLOTS:
            ocupado = hora in horas_ocupadas
            if fecha == hoy and hora <= ahora.hour:
                ocupado = True
            slots.append({
                'hora': hora,
                'label': f'{hora:02d}:00',
                'disponible': not ocupado,
            })

        return JsonResponse({'slots': slots, 'fecha': fecha_str})


# ── API: precio de paquete con descuento ──────────────────────────────────────

class PrecioCitaView(LoginRequiredMixin, View):
    """
    GET /citas/api/precio/?cita_id=1
    Devuelve el precio del paquete con descuento si aplica.
    """
    http_method_names = ['get']

    def get(self, request):
        cita_id = request.GET.get('cita_id')
        if not cita_id:
            return JsonResponse({'error': 'Falta cita_id'}, status=400)

        try:
            cita = Cita.objects.select_related('paquete').get(pk=cita_id)
        except Cita.DoesNotExist:
            return JsonResponse({'error': 'Cita no encontrada'}, status=404)

        paquete = cita.paquete

        from apps.servicios.models import Promocion
        from django.db.models import Sum

        # precio base = suma de precios de los servicios del paquete
        precio_original = float(
            paquete.servicios.aggregate(total=Sum('precio'))['total'] or 0
        )
        precio_final = precio_original
        descuento_pct = 0
        promo_nombre = None

        # buscar promoción activa y vigente para el paquete
        hoy = timezone.localdate()
        promo = Promocion.objects.filter(
            paquete=paquete,
            activa=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
        ).first()

        if promo:
            descuento_pct = float(promo.descuento_pct)
            precio_final = round(precio_original * (1 - descuento_pct / 100), 2)
            promo_nombre = promo.descripcion

        return JsonResponse({
            'precio_original': precio_original,
            'descuento_pct': descuento_pct,
            'precio_final': precio_final,
            'promo': promo_nombre,
        })

class CitaPaquetePersonalizadoCreateView(LoginRequiredMixin, CreateView):
    model = Cita
    form_class = CitaForm
    template_name = 'citas/paquete_personalizado_cita.html'
    success_url = reverse_lazy('citas:lista')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['paquete'].required = False  # ← esta línea es el fix
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_servicios'] = PaquetePersonalizadoForm(self.request.POST or None)
        context['form_cita'] = context['form']
        context['hoy'] = date.today().isoformat()
        return context
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form_cita = self.get_form()
        form_servicios = PaquetePersonalizadoForm(request.POST)
        if form_cita.is_valid() and form_servicios.is_valid():
            cita = form_cita.save(commit=False)
            cita.cliente = request.user
            cita.paquete = None

            servicios_seleccionados = form_servicios.cleaned_data['servicios']
            total_calculado = sum(servicio.precio for servicio in servicios_seleccionados)
            cita.precio_total = total_calculado
            cita.save()

            if hasattr(cita, 'servicios'):
                cita.servicios.set(servicios_seleccionados)

            messages.success(request, f"¡Cita agendada con éxito! Tu combo personalizado incluye {servicios_seleccionados.count()} servicios por un total de ${total_calculado} MXN.")
            return redirect(self.success_url)

        messages.error(request, "No fue posible agendar la cita. Revisa los errores marcados en el formulario.")
        return self.render_to_response(
            self.get_context_data(form=form_cita, form_servicios=form_servicios)
        )