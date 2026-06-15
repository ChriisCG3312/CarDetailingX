"""Formularios del módulo de Seguimiento."""
from django import forms
from .models import Seguimiento


class SeguimientoForm(forms.ModelForm):
    class Meta:
        model = Seguimiento
        fields = ('cita', 'tecnico', 'estado_actual', 'notas', 'foto_antes', 'foto_despues')
        widgets = {
            'cita': forms.Select(attrs={'class': 'form-select'}),
            'tecnico': forms.Select(attrs={'class': 'form-select'}),
            'estado_actual': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'foto_antes': forms.FileInput(attrs={'class': 'form-control'}),
            'foto_despues': forms.FileInput(attrs={'class': 'form-control'}),
        }
