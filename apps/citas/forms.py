"""Formularios del módulo de Citas."""
from django import forms
from django.utils import timezone

from apps.servicios.models import Paquete
from .models import Cita, Vehiculo, Pago


HORA_APERTURA = 8
HORA_CIERRE = 18
DIAS_ATENCION = set(range(6))  # lunes=0 … sábado=5


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ('marca', 'modelo', 'anio', 'color', 'placas', 'foto')
        widgets = {
            'marca': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Ej. Honda'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Ej. Civic'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control', 'min': 1990, 'required': True, 'placeholder': 'Ej. 2020'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Ej. Blanco'}),
            'placas': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Ej. ABC-123-D'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_anio(self):
        anio = self.cleaned_data['anio']
        actual = timezone.now().year
        if not (1990 <= anio <= actual + 1):
            raise forms.ValidationError("El año del vehículo no es válido")
        return anio

    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if not foto or not hasattr(foto, 'name'):
            return foto
        ext = foto.name.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png']:
            raise forms.ValidationError("Solo se permiten imágenes JPG o PNG")
        if foto.size > 2 * 1024 * 1024:
            raise forms.ValidationError("La imagen no puede pesar más de 2MB")
        return foto


class CitaForm(forms.ModelForm):
    """
    Formulario de agendado.
    Recibe `usuario` para filtrar solo sus vehículos.
    """

    class Meta:
        model = Cita
        fields = ('vehiculo', 'paquete', 'fecha_hora', 'notas_cliente')
        widgets = {
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'paquete': forms.Select(attrs={'class': 'form-select'}),
            'fecha_hora': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'notas_cliente': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario and not usuario.es_admin:
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(cliente=usuario)
        # solo paquetes activos
        self.fields['paquete'].queryset = Paquete.objects.filter(activo=True, es_personalizado=False)

    def clean_fecha_hora(self):
        fecha_hora = self.cleaned_data.get('fecha_hora')
        if not fecha_hora:
            return fecha_hora

        fecha_hora_local = timezone.localtime(fecha_hora)

        if fecha_hora <= timezone.now():
            raise forms.ValidationError("No puedes agendar una cita en una fecha pasada")

        if fecha_hora_local.weekday() not in DIAS_ATENCION:
            raise forms.ValidationError(
                "El horario de atención es de lunes a sábado de 8:00 a 18:00"
            )

        if not (HORA_APERTURA <= fecha_hora_local.hour < HORA_CIERRE):
            raise forms.ValidationError(
                "El horario de atención es de lunes a sábado de 8:00 a 18:00"
            )

        return fecha_hora

    def clean(self):
        cleaned = super().clean()
        fecha_hora = cleaned.get('fecha_hora')
        paquete = cleaned.get('paquete')
        vehiculo = cleaned.get('vehiculo')

        # validar que el vehículo no tenga ya una cita en proceso
        if vehiculo:
            en_proceso = Cita.objects.filter(
                vehiculo=vehiculo,
                estado=Cita.Estado.EN_PROCESO
            )
            if self.instance.pk:
                en_proceso = en_proceso.exclude(pk=self.instance.pk)
            if en_proceso.exists():
                raise forms.ValidationError(
                    'Este vehículo ya tiene una cita en proceso. '
                    'Espera a que termine antes de agendar otra.'
                )

        if not fecha_hora or not paquete:
            return cleaned

        # disponibilidad — usar duración del primer servicio del paquete
        primer_servicio = paquete.servicios.first()
        if primer_servicio:
            duracion = timezone.timedelta(hours=float(primer_servicio.duracion_horas))
        else:
            duracion = timezone.timedelta(hours=1)

        fin_nueva = fecha_hora + duracion

        traslape = (
            Cita.objects
            .exclude(estado=Cita.Estado.CANCELADA)
            .filter(
                fecha_hora__lt=fin_nueva,
                fecha_hora__gte=fecha_hora - duracion,
            )
        )

        if self.instance.pk:
            traslape = traslape.exclude(pk=self.instance.pk)

        if traslape.exists():
            raise forms.ValidationError("Ya existe una cita en ese horario. Elige otro")

        return cleaned


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
        self.fields['cita'].queryset = (
            Cita.objects
            .filter(estado=Cita.Estado.TERMINADA, pago__isnull=True)
            .select_related('cliente', 'vehiculo', 'paquete')
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