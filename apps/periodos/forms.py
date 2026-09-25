from django import forms

from .models import Periodo


class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ["nombre", "inicio", "fin", "fecha_cierre_propuestas", "cupo_minimo", "abierto"]
        widgets = {
            "inicio": forms.DateInput(attrs={"type": "date"}),
            "fin": forms.DateInput(attrs={"type": "date"}),
            "fecha_cierre_propuestas": forms.DateInput(attrs={"type": "date"}),
        }