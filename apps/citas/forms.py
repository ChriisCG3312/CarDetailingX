"""Formularios del módulo de Citas."""
from django import forms
from .models import Cita, Vehiculo, Pago


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ('marca', 'modelo', 'anio', 'color', 'placas', 'foto')
        widgets = {
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control', 'min': 1990}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'placas': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CitaForm(forms.ModelForm):
    """
    Formulario de agendado.
    Recibe `usuario` para filtrar solo sus vehículos.
    """

    class Meta:
        model = Cita
        fields = ('vehiculo', 'servicio', 'fecha_hora', 'notas_cliente')
        widgets = {
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'servicio': forms.Select(attrs={'class': 'form-select'}),
            'fecha_hora': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'notas_cliente': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario and not usuario.es_admin:
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(cliente=usuario)


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ('cita', 'monto', 'metodo', 'referencia')
        widgets = {
            'cita': forms.Select(attrs={'class': 'form-select'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'metodo': forms.Select(attrs={'class': 'form-select'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # solo citas terminadas sin pago previo (RF-07)
        self.fields['cita'].queryset = (
            Cita.objects
            .filter(estado=Cita.Estado.TERMINADA, pago__isnull=True)
            .select_related('cliente', 'vehiculo', 'servicio')
        )

    def clean_cita(self):
        cita = self.cleaned_data.get('cita')
        if not cita:
            return cita
        if cita.estado != Cita.Estado.TERMINADA:
            raise forms.ValidationError("Solo puedes registrar el pago de citas terminadas")
        if hasattr(cita, 'pago'):
            raise forms.ValidationError("Esta cita ya tiene un pago registrado")
        return cita

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is not None and monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor a $0")
        return monto