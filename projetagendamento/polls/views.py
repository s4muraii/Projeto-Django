from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import ReservaModel, Sala, send_verification_email
from rolepermissions.roles import assign_role
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ReservaSerializer,  CadastroSerializer, SalaSerializer, GerenciarSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import random



class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            # User is valid, now send verification code
            verification_code = random.randint(100000, 999999)
            # Save the verification code in the session
            self.request.session['verification_code'] = verification_code
            # Send the verification code to the user's email
            send_verification_email(user, verification_code)
            return Response({'message': 'Verification code sent'}, status=status.HTTP_200_OK)
        else:
            # Invalid username or password
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyCodeView(APIView):
    def post(self, request):
        verification_code = request.data.get('verification_code')
        if verification_code == self.request.session.get('verification_code'):
            user = User.objects.get(username=request.data.get('username'))
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        
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
                novousuario = User.objects.create_user(username=user, password=senha, email=serializer.validated_data["email"], first_name=serializer.validated_data["nome"])
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