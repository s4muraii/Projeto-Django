from rest_framework import serializers
from .models import ReservaModel,Sala, NIVEL_ACESSO, TIPOS_SALA


class ReservaSerializer(serializers.ModelSerializer):
    responsavel = serializers.CharField(required=False)
    sala = serializers.CharField(required=False)
    class Meta:
        model = ReservaModel
        fields = ['id','sala','responsavel', 'dia', 'hora_inicio', 'hora_fim', 'descricao', 'event_id']
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    senha = serializers.CharField(style={'input_type': 'password'})
    
class CadastroSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(style={'input_type': 'password'})
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=50)  
    last_name = serializers.CharField(max_length=50) 
    nivel_acesso = serializers.ChoiceField(choices=NIVEL_ACESSO)
    
class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = ['nome', 'descricao', 'capacidade', 'tipo', 'projetor', 'ar_condicionado', 'id', 'imagem']
class GerenciarSerializer(serializers.Serializer):
    id = serializers.IntegerField()