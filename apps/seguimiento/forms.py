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
        fields = ['cita', 'tecnico', 'notas_iniciales']
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
        instance = kwargs.get('instance')

        # Limitar opciones de estado: solo hacia adelante
        if instance:
            estados_validos = [
                (v, l) for v, l in Seguimiento.Estado.choices
                if Seguimiento.ORDEN_ESTADOS.index(v)
                >= Seguimiento.ORDEN_ESTADOS.index(instance.estado)
            ]
            self.fields['estado'].widget = forms.Select(
                attrs={'class': 'form-control'},
                choices=estados_validos,
            )

        # Configurar campos de foto según el estado actual
        if instance:
            estado_actual = instance.estado

            if estado_actual == Seguimiento.Estado.RECIBIDO:
                # Foto antes obligatoria — el técnico documenta el estado inicial
                self.fields['foto_antes'].label = 'Foto del vehículo al recibirlo'
                self.fields['foto_antes'].help_text = 'Obligatoria. Documenta el estado del vehículo antes del detallado.'
                self.fields['foto_antes'].required = True
                del self.fields['foto_despues']

            elif estado_actual in (Seguimiento.Estado.LISTO, Seguimiento.Estado.ENTREGADO):
                # Foto después obligatoria — resultado del detallado
                self.fields['foto_despues'].label = 'Foto del vehículo después del detallado'
                self.fields['foto_despues'].help_text = 'Obligatoria. Documenta el resultado final del servicio.'
                self.fields['foto_despues'].required = False
                del self.fields['foto_antes']

            else:
                # Estados intermedios — sin fotos
                del self.fields['foto_antes']
                del self.fields['foto_despues']

        # Estilos Bootstrap a todos los campos restantes
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        nuevo_estado = cleaned_data.get('estado')

        # Validar que no retroceda estado
        if self.instance and self.instance.pk:
            if nuevo_estado and not self.instance.puede_avanzar_a(nuevo_estado) \
                    and nuevo_estado != self.instance.estado:
                raise ValidationError('No puedes regresar a un estado anterior.')

        # Foto antes obligatoria en estado recibido
        if self.instance and self.instance.estado == Seguimiento.Estado.RECIBIDO:
            foto_antes = cleaned_data.get('foto_antes')
            if not foto_antes and not self.instance.foto_antes:
                raise ValidationError(
                    'Debes subir la foto del vehículo antes de continuar.'
                )

        # Foto después obligatoria al marcar listo o entregado
        if nuevo_estado in (Seguimiento.Estado.LISTO, Seguimiento.Estado.ENTREGADO):
            foto_despues = cleaned_data.get('foto_despues')
            if not foto_despues and not self.instance.foto_despues:
                raise ValidationError(
                    'Debes subir la foto del resultado antes de marcarlo como listo o entregado.'
                )

        return cleaned_data