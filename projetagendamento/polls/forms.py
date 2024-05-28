from django import forms
from .models import TIPOS_SALA, ReservaModel, NIVEL_ACESSO, Sala


class VerificacaoDisponibilidadeForm(forms.Form):
    nome_item = forms.CharField(max_length=100)


class AgendarForm(forms.ModelForm):

    def __str__(self):
        return self.nome


class ReservaForm(forms.ModelForm):
    class Meta:
        model = ReservaModel
        fields = ["sala", "data", "hora_inicio", "hora_fim", "responsavel", "descricao"]
        widgets = {
            "sala": forms.Select(choices=TIPOS_SALA, attrs={"class": "input"}),
            "data": forms.DateInput(attrs={"type": "date"}),
            "hora_inicio": forms.TimeInput(attrs={"type": "time"}),
            "hora_fim": forms.TimeInput(attrs={"type": "time"}),
            "responsavel": forms.TextInput(
                attrs={"class": "input", "placeholder": "Responsável"}
            ),
            "descricao": forms.Textarea(
                attrs={"class": "input", "placeholder": "Descrição"}
            ),
        }


class LoginForm(forms.Form):
    username = forms.CharField(
        label="",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "User"}),
    )
    senha = forms.CharField(
        label="",
        max_length=20,
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Senha"}),
    )


class CadastroForm(forms.Form):
    username = forms.CharField(
        label="",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "User"}),
    )
    senha = forms.CharField(
        label="",
        max_length=20,
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Senha"}),
    )
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={"class": "input", "placeholder": "Email"}),
    )
    nome = forms.CharField(
        label="",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Nome"}),
    )
    nivel_acesso = forms.ChoiceField(
        label="",
        choices=NIVEL_ACESSO,
        widget=forms.Select(attrs={"class": "input"}),
    )
    
    
class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ["nome", "descricao", "capacidade", "tipo", "projetor", "ar_condicionado"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "input", "placeholder": "Nome"}),
            "descricao": forms.Textarea(attrs={"class": "input", "placeholder": "Descrição"}),
            "capacidade": forms.NumberInput(attrs={"class": "input", "placeholder": "Capacidade"}),
            "tipo": forms.Select(choices=TIPOS_SALA, attrs={"class": "input"}),
            "projetor": forms.CheckboxInput(attrs={"class": "input"}),
            "ar_condicionado": forms.CheckboxInput(attrs={"class": "input"}),
        }
        