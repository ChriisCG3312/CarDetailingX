"""Formularios del módulo de Servicios."""
from django import forms
from .models import Servicio, Promocion


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
        fields = ('servicio', 'descripcion', 'descuento_pct', 'fecha_inicio', 'fecha_fin', 'activa')
        widgets = {
            'servicio': forms.Select(attrs={'class': 'form-select'}),
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
