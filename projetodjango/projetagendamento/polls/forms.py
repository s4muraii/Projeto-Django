from django import forms
from .models import TIPOS_SALA

class VerificacaoDisponibilidadeForm(forms.Form):
    nome_item = forms.CharField(max_length=100)


