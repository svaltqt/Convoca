from django import forms

from .models import Facultad, Programa


class FacultadForm(forms.ModelForm):
    class Meta:
        model = Facultad
        fields = ("nombre",)


class ProgramaForm(forms.ModelForm):
    class Meta:
        model = Programa
        fields = ("nombre", "codigo", "facultad")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Facultad.objects.filter(activa=True)
        if (
            self.instance.facultad_id
            and not queryset.filter(pk=self.instance.facultad_id).exists()
        ):
            # Conserva la facultad actual en el desplegable aunque ya esté
            # inactiva, para no bloquear la edición de otros campos del
            # programa (regla 21: la desactivación conserva referencias).
            queryset = queryset | Facultad.objects.filter(pk=self.instance.facultad_id)
        self.fields["facultad"].queryset = queryset.order_by("nombre")
