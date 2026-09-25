from typing import ClassVar

from django import forms
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from apps.academico.models import Programa

from .models import Usuario


class FormularioLogin(AuthenticationForm):
    error_messages: ClassVar[dict[str, str]] = {
        "invalid_login": "Correo o contraseña incorrectos. Verifica tus datos e intenta de nuevo.",
        "inactive": "Esta cuenta está inactiva.",
    }


class RegistroForm(forms.ModelForm):
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ("first_name", "last_name", "email", "programa", "autorizo_datos")
        labels: ClassVar[dict[str, str]] = {
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "email": "Correo institucional",
            "programa": "Programa",
            "autorizo_datos": "Autorizo el tratamiento de mis datos personales",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["programa"].queryset = Programa.objects.filter(
            activo=True
        ).order_by("nombre")
        self.fields["programa"].required = True
        self.fields["autorizo_datos"].required = True
        self.fields["autorizo_datos"].error_messages["required"] = (
            "Debe autorizar el tratamiento de sus datos personales para crear la cuenta."
        )
        self.fields["autorizo_datos"].help_text = format_html(
            'Puedes leer la <a href="{}">política de tratamiento de datos</a> antes de continuar.',
            reverse("usuarios:politica_datos"),
        )
        self.order_fields(
            [
                "first_name",
                "last_name",
                "email",
                "programa",
                "password",
                "autorizo_datos",
            ]
        )

    def clean_email(self):
        email = self.cleaned_data["email"]
        dominio = settings.DOMINIO_INSTITUCIONAL
        if not email.lower().endswith(f"@{dominio}"):
            raise forms.ValidationError(
                f"El correo debe pertenecer al dominio institucional @{dominio}."
            )
        return email

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get("password")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error("password", error)

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])
        if usuario.autorizo_datos:
            usuario.fecha_autorizacion = timezone.now()
        if commit:
            usuario.save()
        return usuario


class UsuarioForm(forms.ModelForm):
    """
    Edición administrativa de una cuenta (HU-07): solo nombre, apellido y
    programa. Nunca incluye la contraseña ni la autorización de datos, que
    solo el propio usuario otorga al registrarse.
    """

    class Meta:
        model = Usuario
        fields = ("first_name", "last_name", "programa")
        labels: ClassVar[dict[str, str]] = {
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "programa": "Programa",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Programa.objects.filter(activo=True)
        if (
            self.instance.programa_id
            and not queryset.filter(pk=self.instance.programa_id).exists()
        ):
            queryset = queryset | Programa.objects.filter(pk=self.instance.programa_id)
        self.fields["programa"].queryset = queryset.order_by("nombre")
        self.fields["programa"].empty_label = "Sin programa asignado"
