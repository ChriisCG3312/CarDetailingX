"""Formularios del módulo de Servicios."""
from django import forms
from .models import Servicio, Promocion
from .models import Paquete


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ('nombre', 'descripcion', 'precio', 'duracion_horas', 'activo', 'imagen')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'duracion_horas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PromocionForm(forms.ModelForm):
    class Meta:
        model = Promocion
        fields = ['nombre', 'paquete', 'descripcion', 'descuento_pct', 'fecha_inicio', 'fecha_fin', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Combo Verano'}),
            'paquete': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'descuento_pct': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get('fecha_inicio')
        fin = cleaned.get('fecha_fin')
        if inicio and fin and fin < inicio:
            raise forms.ValidationError('La fecha de fin no puede ser anterior a la de inicio.')
        return cleaned


class PaqueteForm(forms.ModelForm):
    # Campo extra independiente para aplicar el descuento al momento de crear
    descuento_promocion = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        min_value=0,
        max_value=100,
        label="Descuento Inicial (%)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 10.00 (Dejar vacío o en 0 si no lleva)'})
    )

    class Meta:
        model = Paquete
        fields = ['nombre', 'descripcion', 'servicios', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Combo Pulido Premium'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe qué incluye este paquete...'}),
            'servicios': forms.SelectMultiple(attrs={'class': 'form-select', 'help_text': 'Mantén presionado Ctrl para seleccionar varios'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }