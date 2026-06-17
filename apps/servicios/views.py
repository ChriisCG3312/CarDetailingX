"""
Vistas del módulo de Servicios y Promociones.
Responsable: D2
"""
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .forms import ServicioForm, PromocionForm, PaqueteForm, PaquetePersonalizadoForm

from .models import Servicio, Promocion, Paquete
from .forms import ServicioForm, PromocionForm, PaqueteForm
from apps.usuarios.mixins import AdminRequiredMixin, LoginRequiredMixin

from django.shortcuts import render, redirect


# ── Servicios ─────────────────────────────────────────────────────────────────

class ServicioListView(ListView):
    """Vista pública del catálogo de servicios (accesible sin login)."""
    model = Servicio
    template_name = 'servicios/lista.html'
    context_object_name = 'paquetes'

    def get_queryset(self):
        return Paquete.objects.filter(activo=True, es_personalizado=False)


class ServicioAdminListView(AdminRequiredMixin, ListView):
    """Lista de servicios para el administrador (incluye inactivos)."""
    model = Servicio
    template_name = 'servicios/admin_lista.html'
    context_object_name = 'servicios'


class ServicioCreateView(AdminRequiredMixin, CreateView):
    model = Servicio
    form_class = ServicioForm
    template_name = 'servicios/form.html'
    success_url = reverse_lazy('servicios:admin_lista')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nuevo servicio'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Servicio creado correctamente.')
        return super().form_valid(form)


class ServicioUpdateView(AdminRequiredMixin, UpdateView):
    model = Servicio
    form_class = ServicioForm
    template_name = 'servicios/form.html'
    success_url = reverse_lazy('servicios:admin_lista')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar: {self.object.nombre}'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Servicio actualizado.')
        return super().form_valid(form)


class ServicioDeleteView(AdminRequiredMixin, DeleteView):
    model = Servicio
    template_name = 'servicios/confirmar_eliminar.html'
    success_url = reverse_lazy('servicios:admin_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Servicio eliminado.')
        return super().form_valid(form)


# ── Promociones ───────────────────────────────────────────────────────────────

class PromocionListView(AdminRequiredMixin, ListView):
    model = Promocion
    template_name = 'servicios/promociones_lista.html'
    context_object_name = 'promociones'


class PromocionCreateView(AdminRequiredMixin, CreateView):
    model = Promocion
    form_class = PromocionForm
    template_name = 'servicios/promocion_form.html'
    success_url = reverse_lazy('servicios:promociones')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nueva promoción'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Promoción creada.')
        return super().form_valid(form)


class PromocionUpdateView(AdminRequiredMixin, UpdateView):
    model = Promocion
    form_class = PromocionForm
    template_name = 'servicios/promocion_form.html'
    success_url = reverse_lazy('servicios:promociones')

    def form_valid(self, form):
        messages.success(self.request, 'Promoción actualizada.')
        return super().form_valid(form)


class PromocionDeleteView(AdminRequiredMixin, DeleteView):
    model = Promocion
    template_name = 'servicios/confirmar_eliminar.html'
    success_url = reverse_lazy('servicios:promociones')

    def form_valid(self, form):
        messages.success(self.request, 'Promoción eliminada.')
        return super().form_valid(form)

from datetime import datetime

# ==========================================
# — Paquetes
# ==========================================

class PaqueteAdminListView(AdminRequiredMixin, ListView):
    """Lista de paquetes para el administrador (excluye personalizados)."""
    model = Paquete
    template_name = 'servicios/paquete_admin_list.html'
    context_object_name = 'paquetes'

    def get_queryset(self):
        return Paquete.objects.filter(es_personalizado=False)


class PaqueteCreateView(AdminRequiredMixin, CreateView):
    """Crea un nuevo paquete y genera una promoción automática si lleva descuento."""
    model = Paquete
    form_class = PaqueteForm
    template_name = 'servicios/paquete_form.html'
    success_url = reverse_lazy('servicios:paquete_admin_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nuevo paquete'
        return ctx

    def form_valid(self, form):
        # 1. Guarda el paquete en la base de datos primero
        response = super().form_valid(form)
        
        # 2. Revisa si el usuario digitó un descuento en el campo extra
        descuento = form.cleaned_data.get('descuento_promocion')
        if descuento and descuento > 0:
            Promocion.objects.create(
                nombre=f"Descuento {self.object.nombre}",
                paquete=self.object,
                descripcion=f"Descuento aplicado al paquete {self.object.nombre}",
                descuento_pct=descuento,
                fecha_inicio=datetime.now().date(),
                fecha_fin=datetime.now().date().replace(year=datetime.now().year + 1), # Vigencia por defecto de 1 año
                activa=True
            )
            messages.success(self.request, f"Paquete '{self.object.nombre}' creado con éxito con descuento del {descuento}%.")
        else:
            messages.success(self.request, f"Paquete '{self.object.nombre}' creado correctamente sin descuento.")
            
        return response


class PaqueteUpdateView(AdminRequiredMixin, UpdateView):
    """Edita un paquete existente."""
    model = Paquete
    form_class = PaqueteForm
    template_name = 'servicios/paquete_form.html'
    success_url = reverse_lazy('servicios:paquete_admin_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f"Editar: {self.object.nombre}"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Paquete actualizado correctamente.')
        return super().form_valid(form)


class PaqueteDeleteView(AdminRequiredMixin, DeleteView):
    """Elimina o desactiva un paquete."""
    model = Paquete
    template_name = 'servicios/confirmar_eliminar.html'
    success_url = reverse_lazy('servicios:paquete_admin_list')

    def form_valid(self, form):
        messages.success(self.request, 'Paquete eliminado correctamente.')
        return super().form_valid(form)

class PaquetePersonalizadoCreateView(LoginRequiredMixin, CreateView):
    """Permite al cliente diseñar su propio paquete seleccionando múltiples servicios."""
    model = Paquete
    form_class = PaquetePersonalizadoForm
    template_name = 'servicios/paquete_personalizado_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Diseñar mi paquete'
        return ctx

    def form_valid(self, form):
        # Creamos la instancia en memoria sin guardarla en la BD todavía
        paquete = form.save(commit=False)
        
        # Automatizamos los datos del paquete personalizado
        paquete.nombre = f"Personalizado - {self.request.user.username}"
        paquete.descripcion = f"Paquete a la medida diseñado por el cliente {self.request.user.get_full_name() or self.request.user.username}"
        paquete.es_personalizado = True
        paquete.activo = True
        
        # Guardamos el paquete en la BD para generar su ID
        paquete.save()
        
        # Guardamos las relaciones ManyToMany (los servicios seleccionados)
        form.save_m2m()
        
        messages.success(self.request, "¡Tu paquete personalizado ha sido diseñado! Procede a elegir fecha y hora para tu cita.")
        
        # Redirigimos al flujo de citas pasándole el ID del paquete en la URL
        return redirect(f"{reverse_lazy('citas:crear')}?paquete_id={paquete.id}")