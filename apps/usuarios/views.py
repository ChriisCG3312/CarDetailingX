"""
Vistas de autenticación y gestión de usuarios.
Responsable: D1
"""
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, View

from .forms import LoginForm, RegistroUsuarioForm, UsuarioAdminForm
from .models import Usuario
from apps.usuarios.mixins import AdminRequiredMixin


# ── Autenticación ──────────────────────────────────────────────────────────────

class LoginView(View):
    """Vista de inicio de sesión."""
    template_name = 'usuarios/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        from django.shortcuts import render
        return render(request, self.template_name, {'form': LoginForm()})

    def post(self, request):
        from django.shortcuts import render
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f'Bienvenido, {form.get_user().first_name or form.get_user().username}.')
            return redirect(request.GET.get('next', 'dashboard:home'))
        return render(request, self.template_name, {'form': form})


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
        if rol:
            qs = qs.filter(rol=rol)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['roles'] = Usuario.Rol.choices
        ctx['rol_activo'] = self.request.GET.get('rol', '')
        return ctx


class UsuarioCreateView(AdminRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioAdminForm
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
    form_class = UsuarioAdminForm
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuarios:lista')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar usuario: {self.object}'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado.')
        return super().form_valid(form)


class UsuarioDeleteView(AdminRequiredMixin, DeleteView):
    model = Usuario
    template_name = 'usuarios/confirmar_eliminar.html'
    success_url = reverse_lazy('usuarios:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario eliminado.')
        return super().form_valid(form)
