"""
Módulo: Usuarios
Responsable: D1

Modelos:
- Usuario: extiende AbstractUser con rol y teléfono.
- Perfil de cliente se maneja desde apps.citas (ver Cliente).
"""
import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


def usuario_foto_path(instance, filename):
    extension = os.path.splitext(filename)[1].lower()

    return (
        f'usuarios/fotos/'
        f'{uuid.uuid4().hex}'
        f'{extension}'
    )


class Usuario(AbstractUser):
    """
    Usuario personalizado del sistema Detailing.
    Extiende AbstractUser para agregar rol y teléfono.
    """

    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        CLIENTE = 'cliente', 'Cliente'
        TECNICO = 'tecnico', 'Técnico'

    rol = models.CharField(
        max_length=10,
        choices=Rol.choices,
        default=Rol.CLIENTE,
        verbose_name='Rol',
    )

    telefono = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Teléfono',
    )

    foto = models.ImageField(
        upload_to=usuario_foto_path,
        blank=True,
        null=True,
        verbose_name='Foto de perfil',
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return (
            f'{self.get_full_name() or self.username} '
            f'({self.get_rol_display()})'
        )

    def save(self, *args, **kwargs):
        if self.pk:
            anterior = Usuario.objects.filter(pk=self.pk).first()

            if (
                anterior and
                anterior.foto and
                self.foto and
                anterior.foto != self.foto
            ):
                anterior.foto.delete(save=False)

        super().save(*args, **kwargs)

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN

    @property
    def es_cliente(self):
        return self.rol == self.Rol.CLIENTE

    @property
    def es_tecnico(self):
        return self.rol == self.Rol.TECNICO