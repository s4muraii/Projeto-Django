from rest_framework import serializers
from .models import ReservaModel,Sala, NIVEL_ACESSO, TIPOS_SALA


class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaModel
        fields = ['sala', 'data', 'hora_inicio', 'hora_fim', 'descricao']
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    senha = serializers.CharField(style={'input_type': 'password'})
    
class CadastroSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    senha = serializers.CharField(style={'input_type': 'password'})
    email = serializers.EmailField()
    nome = serializers.CharField(max_length=50)
    nivel_acesso = serializers.ChoiceField(choices=NIVEL_ACESSO)
    
class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = ['nome', 'descricao', 'capacidade', 'tipo', 'projetor', 'ar_condicionado']
class GerenciarSerializer(serializers.Serializer):
    id = serializers.IntegerField()