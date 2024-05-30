from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ReservaModel, Sala
from rolepermissions.roles import assign_role
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ReservaSerializer, LoginSerializer, CadastroSerializer, SalaSerializer, GerenciarSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated


@method_decorator(csrf_exempt, name='dispatch')
class LogarView(APIView):
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return Response({"message": "Login realizado com sucesso!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Login ou senha inválidos!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReservaView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        serializer = ReservaSerializer(data=request.data)
        if serializer.is_valid():
            horarios_existentes = ReservaModel.objects.filter(
                sala=serializer.validated_data["sala"],
                data=serializer.validated_data["data"],
                hora_inicio__lt=serializer.validated_data["hora_fim"],
                hora_fim__gt=serializer.validated_data["hora_inicio"],
                descricao = serializer.validated_data["descricao"]
            )
            if horarios_existentes.exists():
                return Response({"message": "Horário indisponível!"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer.save(responsavel=request.user.username)
                return Response({"message": "Reserva realizada com sucesso!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LogarView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('senha')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return Response({"message": "Login realizado com sucesso!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Login ou senha inválidos!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required, name='dispatch')
class CadastroView(APIView):
    def post(self, request, format=None):
        if not (request.user.groups.filter(name='SuperAdmin').exists() or request.user.groups.filter(name='secretaria').exists()):
            return Response("Você não tem permissão para acessar essa página!", status=status.HTTP_403_FORBIDDEN)
        serializer = CadastroSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["username"]
            senha = serializer.validated_data["senha"]
            if (User.objects.filter(username=user).exists() or User.objects.filter(email=user).exists()):
                return Response("Informações já cadastradas!", status=status.HTTP_400_BAD_REQUEST)
            if request.user.groups.filter(name='SuperAdmin').exists():
                nivel_acesso = serializer.validated_data["nivel_acesso"]
                novousuario = User.objects.create_user(username=user, password=senha)
                novousuario.save()
                assign_role(novousuario, nivel_acesso)
            else:
                nivel_acesso = "funcionario"
                novousuario = User.objects.create_user(username=user, password=senha)
                novousuario.save()
                assign_role(novousuario, nivel_acesso)
            return Response(f"{nivel_acesso} cadastradado com sucesso!", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(login_required, name='dispatch')
class ListarSalas(APIView):
    def get(self, request, format= None):
        salas = Sala.objects.all()
        serializer = SalaSerializer(salas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@method_decorator(login_required, name='dispatch')
class GerenciarReservas(APIView):
    def get(self, request, format=None):
        if not (request.user.groups.filter(name='SuperAdmin').exists() or request.user.groups.filter(name='secretaria').exists()):
            return Response("Você não tem permissão para acessar essa página!", status=status.HTTP_403_FORBIDDEN)
        reservas = ReservaModel.objects.all()
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        if not (request.user.groups.filter(name='SuperAdmin').exists() or request.user.groups.filter(name='secretaria').exists()):
            return Response("Você não tem permissão para acessar essa página!", status=status.HTTP_403_FORBIDDEN)
        else:
            serializer = GerenciarSerializer(data=request.data)
            if serializer.is_valid():
                reserva_id = serializer.validated_data["id"]
                reserva = ReservaModel.objects.get(id=reserva_id)
                reserva.delete()
        return Response("Reserva excluída com sucesso!", status=status.HTTP_200_OK)
    


@method_decorator(login_required, name='dispatch')
class EditarReservas(APIView):
    def get (self, request, id, format=None):
        if not (request.user.groups.filter(name='SuperAdmin').exists() or request.user.groups.filter(name='secretaria').exists()):
            return Response("Você não tem permissão para acessar essa página!", status=status.HTTP_403_FORBIDDEN)
        try:
            reserva = ReservaModel.objects.get(id=id)
        except ReservaModel.DoesNotExist:
            return Response(f"Reserva não encontrada!", status=status.HTTP_404_NOT_FOUND)
        serializer = ReservaSerializer(reserva)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request, id, format=None):
        if not (request.user.groups.filter(name='SuperAdmin').exists() or request.user.groups.filter(name='secretaria').exists()):
            return Response("Você não tem permissão para acessar essa página!", status=status.HTTP_403_FORBIDDEN)
        try:
            reserva = ReservaModel.objects.get(id=id)
        except ReservaModel.DoesNotExist:
            return Response("Reserva não encontrada!", status=status.HTTP_404_NOT_FOUND)
        serializer = ReservaSerializer(reserva, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@method_decorator(login_required, name='dispatch')
class CadastrarSalas(APIView):
    def post(self, request, format=None):
        if not (request.user.groups.filter(name='SuperAdmin').exists() or request.user.groups.filter(name='secretaria').exists()):
            return Response("Você não tem permissão para acessar essa página!", status=status.HTTP_403_FORBIDDEN)
        serializer = SalaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class FiltroHorarios(APIView):
    def post(self, request, format=None):
        data = request.data["data"]
        reservas_filtradas = ReservaModel.objects.filter(data=data)
        serializer = ReservaSerializer(reservas_filtradas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)