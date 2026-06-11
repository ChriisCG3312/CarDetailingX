"""Formularios del módulo de Seguimiento."""
from django import forms
from django.core.exceptions import ValidationError
from .models import Seguimiento
from apps.citas.models import Cita
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class SeguimientoCrearForm(forms.ModelForm):
    """Formulario para que el admin asigne un técnico a una cita confirmada."""

    class Meta:
        model = Seguimiento
        fields = ['cita', 'tecnico', 'notas_iniciales', 'foto_antes']
        widgets = {
            'notas_iniciales': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo citas confirmadas SIN seguimiento previo
        self.fields['cita'].queryset = Cita.objects.filter(
            estado=Cita.Estado.CONFIRMADA
        ).exclude(
            seguimiento__isnull=False
        ).select_related('cliente', 'servicio', 'vehiculo')

        # Solo técnicos activos
        self.fields['tecnico'].queryset = Usuario.objects.filter(
            rol='tecnico', is_active=True
        )

        # Estilos Bootstrap
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_cita(self):
        cita = self.cleaned_data.get('cita')
        if cita and cita.estado != Cita.Estado.CONFIRMADA:
            raise ValidationError('Solo puedes iniciar seguimiento en citas confirmadas.')
        if cita and hasattr(cita, 'seguimiento'):
            raise ValidationError('Esta cita ya tiene un seguimiento asignado.')
        return cita


class SeguimientoActualizarForm(forms.ModelForm):
    """Formulario para que el técnico actualice el estado del servicio."""

    class Meta:
        model = Seguimiento
        fields = ['estado', 'notas_tecnico', 'foto_antes', 'foto_despues']
        widgets = {
            'notas_tecnico': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Estilos Bootstrap
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        # foto_antes solo editable si estado es recibido
        instance = kwargs.get('instance')
        if instance:
            if instance.estado != Seguimiento.Estado.RECIBIDO:
                self.fields['foto_antes'].disabled = True

            # foto_despues solo si estado es listo o entregado
            if instance.estado not in (
                Seguimiento.Estado.LISTO,
                Seguimiento.Estado.ENTREGADO,
            ):
                self.fields['foto_despues'].disabled = True

            # Limitar opciones de estado: solo hacia adelante
            estados_validos = [
                (v, l) for v, l in Seguimiento.Estado.choices
                if Seguimiento.ORDEN_ESTADOS.index(v)
                >= Seguimiento.ORDEN_ESTADOS.index(instance.estado)
            ]
            self.fields['estado'].widget = forms.Select(
                attrs={'class': 'form-control'},
                choices=estados_validos,
            )

    def clean_estado(self):
        nuevo_estado = self.cleaned_data.get('estado')
        if self.instance and self.instance.pk:
            if not self.instance.puede_avanzar_a(nuevo_estado) \
                    and nuevo_estado != self.instance.estado:
                raise ValidationError('No puedes regresar a un estado anterior.')
        return nuevo_estado