"""Formularios de autenticación y registro de usuarios."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate
from .models import Usuario
from django.core.exceptions import ValidationError




class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario o correo",
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        )
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        )
    )

    error_messages = {
        "invalid_login": "Credenciales incorrectas",
        "inactive": "Tu cuenta está desactivada. Contacta al administrador",
    }

    def clean(self):
        usuario_input = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if usuario_input and password:

            usuario = Usuario.objects.filter(
                email__iexact=usuario_input
            ).first()

            if usuario is None:
                usuario = Usuario.objects.filter(
                    username=usuario_input
                ).first()

            if usuario and not usuario.is_active:
                raise forms.ValidationError(
                    "Tu cuenta está desactivada. Contacta al administrador"
                )

            username = usuario.username if usuario else usuario_input

            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )

            if self.user_cache is None:
                raise forms.ValidationError(
                    "Usuario o contraseña incorrectos"
                )

        return self.cleaned_data

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        label="Correo electrónico",
        required=True
    )

    class Meta:
        model = Usuario
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "telefono",
            "password1",
            "password2",
        )

        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
        }

    error_messages = {
        "password_mismatch": "Las contraseñas no coinciden",
    }

    def clean_username(self):
        username = self.cleaned_data["username"]

        if " " in username:
            raise ValidationError(
                "El nombre de usuario no puede contener espacios"
            )

        if Usuario.objects.filter(username=username).exists():
            raise ValidationError(
                "Este nombre de usuario ya está en uso"
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if Usuario.objects.filter(email=email).exists():
            raise ValidationError(
                "Ya existe una cuenta con este correo"
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        password = cleaned_data.get("password1")

        if password:
            if len(password) < 8:
                self.add_error(
                    "password1",
                    "La contraseña debe tener al menos 8 caracteres"
                )

            if password.isdigit():
                self.add_error(
                    "password1",
                    "La contraseña no puede ser solo numérica"
                )

            if username and password == username:
                self.add_error(
                    "password1",
                    "La contraseña no puede ser igual al nombre de usuario"
                )

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)

        usuario.email = self.cleaned_data["email"]
        usuario.rol = Usuario.Rol.CLIENTE

        if commit:
            usuario.save()

        return usuario

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
