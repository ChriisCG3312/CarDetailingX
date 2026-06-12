"""
Vistas de autenticación y gestión de usuarios.
Responsable: D1
"""
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, View
from django.db.models import Q
from .forms import LoginForm, RegistroUsuarioForm, UsuarioAdminCreateForm, UsuarioAdminEditForm
from .models import Usuario
from apps.usuarios.mixins import AdminRequiredMixin


# ── Autenticación ──────────────────────────────────────────────────────────────

class LoginView(View):
    template_name = "usuarios/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard:home")

        return render(
            request,
            self.template_name,
            {
                "form": LoginForm(),
                "next": request.GET.get("next", ""),
            }
        )
    def _registrar_intento_fallido(self, request):
        intentos = request.session.get("login_attempts", 0) + 1

        request.session["login_attempts"] = intentos

        if intentos >= 5:
            messages.warning(
                request,
                "Has tenido varios intentos fallidos de inicio de sesión."
        )

    def post(self, request):
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            request.session["login_attempts"] = 0

            messages.success(
                request,
                f"Bienvenido, {form.get_user().first_name or form.get_user().username}."
            )

            return redirect(
                request.POST.get("next") or "dashboard:home"
            )

        self._registrar_intento_fallido(request)

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "next": request.POST.get("next", ""),
            }
        )

class LogoutView(LoginRequiredMixin, View):
    """Vista de cierre de sesión."""
    def post(self, request):
        logout(request)
        messages.info(request, 'Sesión cerrada correctamente.')
        return redirect('usuarios:login')

class RegistroView(CreateView):
    form_class = RegistroUsuarioForm
    template_name = "usuarios/registro.html"
    success_url = reverse_lazy("usuarios:login")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Cuenta creada correctamente. Ahora puedes iniciar sesión."
        )

        return response

# ── CRUD de Usuarios (solo Admin) ─────────────────────────────────────────────

class UsuarioListView(AdminRequiredMixin, ListView):
    model = Usuario
    template_name = 'usuarios/lista.html'
    context_object_name = 'usuarios'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()

        rol = self.request.GET.get('rol')
        busqueda = self.request.GET.get('q')

        if rol:
            qs = qs.filter(rol=rol)

        if busqueda:
            qs = qs.filter(
                Q(first_name__icontains=busqueda) |
                Q(last_name__icontains=busqueda) |
                Q(email__icontains=busqueda)
            )

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['roles'] = Usuario.Rol.choices
        ctx['rol_activo'] = self.request.GET.get('rol', '')
        ctx['q'] = self.request.GET.get('q', '')
        return ctx

class UsuarioCreateView(AdminRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioAdminCreateForm
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuarios:lista')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Crear usuario'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado correctamente.')
        return super().form_valid(form)

class UsuarioUpdateView(AdminRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioAdminEditForm
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuarios:lista')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.object.pk == self.request.user.pk:
            form.fields['rol'].disabled = True
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar usuario: {self.object}'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado.')
        return super().form_valid(form)

class UsuarioReactivateView(AdminRequiredMixin, View):
    template_name = 'usuarios/confirmar_reactivar.html'

    def get(self, request, pk):
        usuario = get_object_or_404(
            Usuario,
            pk=pk
        )

        return render(
            request,
            self.template_name,
            {
                'object': usuario,
            }
        )

    def post(self, request, pk):
        usuario = get_object_or_404(
            Usuario,
            pk=pk
        )

        usuario.is_active = True
        usuario.save()

        messages.success(
            request,
            'Usuario reactivado correctamente.'
        )

        return redirect('usuarios:lista')

class UsuarioDeleteView(AdminRequiredMixin, DeleteView):
    model = Usuario
    template_name = 'usuarios/confirmar_eliminar.html'
    success_url = reverse_lazy('usuarios:lista')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object == request.user:
            messages.error(
                request,
                'No puedes desactivar tu propia cuenta.'
            )
            return redirect('usuarios:lista')

        self.object.is_active = False
        self.object.save()

        messages.success(
            request,
            'Usuario desactivado correctamente.'
        )

        return redirect(self.success_url)