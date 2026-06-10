"""Formularios de autenticación y registro de usuarios."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Usuario


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión con estilos Bootstrap."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    username = forms.CharField(
        label='Usuario o correo',
        widget=forms.TextInput(attrs={'autofocus': True}),
    )


class RegistroUsuarioForm(UserCreationForm):
    """Formulario de registro público (crea clientes por defecto)."""

    email = forms.EmailField(required=True, label='Correo electrónico')
    first_name = forms.CharField(max_length=50, required=True, label='Nombre')
    last_name = forms.CharField(max_length=50, required=True, label='Apellido')
    telefono = forms.CharField(max_length=15, required=False, label='Teléfono')

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono',
                  'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = Usuario.Rol.CLIENTE  # Registro público siempre es cliente
        if commit:
            user.save()
        return user


class UsuarioAdminForm(forms.ModelForm):
    """Formulario para que el Admin cree/edite cualquier usuario."""

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email',
                  'telefono', 'rol', 'is_active', 'foto')
        widgets = {
            field: forms.TextInput(attrs={'class': 'form-control'})
            for field in ('username', 'first_name', 'last_name', 'email', 'telefono')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not hasattr(field.widget, 'attrs'):
                continue
            field.widget.attrs.setdefault('class', 'form-control')
