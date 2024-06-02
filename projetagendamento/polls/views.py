from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ReservaModel, Sala, send_verification_email, get_id_by_token, create_google_calendar_event, delete_google_calendar_event, update_google_calendar_event, CALENDAR_IDS
from rolepermissions.roles import assign_role
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ReservaSerializer,  CadastroSerializer, SalaSerializer, GerenciarSerializer
from django.utils.decorators import method_decorator
from rest_framework.decorators import permission_classes
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
import random
from django.db.models import Q



class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            # User is valid, now send verification code
            verification_code = random.randint(100000, 999999)
            # Save the verification code in the cache with a key that includes the username
            cache.set(f'verification_code_{username}', verification_code, timeout=300)
            print(f"Sent verification code: {verification_code}")
            # Send the verification code to the user's email
            send_verification_email(user, verification_code)
            return Response({'message': 'Verification code sent'}, status=status.HTTP_200_OK)
        else:
            # Invalid username or password
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)

class VerifyCodeView(APIView):
    def post(self, request):
        username = request.data.get('username')
        verification_code = request.data.get('verification_code')
        # Get the verification code from the cache using a key that includes the username
        stored_code = cache.get(f'verification_code_{username}')
        print(f"Received verification code: {verification_code}")
        print(f"Stored verification code: {stored_code}")
        if verification_code == stored_code:
            user = User.objects.get(username=username)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        
class ReservaView(APIView):
    def post(self, request, format=None):
        try:
            user_id = get_id_by_token(request)
            user = User.objects.get(id=user_id)
            if not user :
                return Response("Você não tem permissão para acessar essa página!", status=status.HTTP_403_FORBIDDEN)
            serializer = ReservaSerializer(data=request.data)
            print(request.data)
            if serializer.is_valid():
                horarios_existentes = ReservaModel.objects.filter(
                    sala=serializer.validated_data["sala"],
                    dia=serializer.validated_data["dia"],
                ).filter(
                    Q(hora_inicio__lt=serializer.validated_data["hora_fim"], hora_fim__gt=serializer.validated_data["hora_inicio"]) |  # reserva existente durante nova reserva
                    Q(hora_inicio__gte=serializer.validated_data["hora_inicio"], hora_fim__lte=serializer.validated_data["hora_fim"])  # nova reserva durante reserva existente
                )
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            if horarios_existentes.exists():
                    return Response({"message": "Horário indisponível!"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                    #Combinar dia com hora_inicio e hora_fim para criar objetos datetime completos
                    start_datetime = datetime.combine(serializer.validated_data["dia"], serializer.validated_data["hora_inicio"])
                    end_datetime = datetime.combine(serializer.validated_data["dia"], serializer.validated_data["hora_fim"])
                    sala_id = int(serializer.validated_data["sala"])
                    sala = Sala.objects.get(id=sala_id)
                    event = create_google_calendar_event(
                        summary=f"Reserva de {user.username} sala {sala.nome}",
                        description=serializer.validated_data["descricao"],
                        start_time=start_datetime,
                        end_time=end_datetime,
                        CalendarID= CALENDAR_IDS[sala_id - 1]
                    )
                    serializer.save(responsavel=user.username, event_id=event['id'], sala=sala)
                    return Response({"message": "Reserva realizada com sucesso!"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

@permission_classes([IsAuthenticated])
class CadastroView(APIView):
    def get (self, request, format=None):
        user_id = get_id_by_token(request)
        user = User.objects.get(id=user_id)
        
        if not (user.groups.filter(name='SuperAdmin').exists() or user.groups.filter(name='secretaria').exists()):
            return Response("Você não tem permissão para acessar essa página!", status=status.HTTP_403_FORBIDDEN)
        nivel_acesso = user.groups.all()[0].name
        return Response({
            'message': 'Você tem permissão para acessar essa página!',
            'nivel_acesso': nivel_acesso
            }, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        serializer = CadastroSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["username"]
            senha = serializer.validated_data["password"]
            email = serializer.validated_data["email"]
            nome = serializer.validated_data["first_name"]
            sobrenome = serializer.validated_data["last_name"]
            nivel_acesso = serializer.validated_data["nivel_acesso"]
            
            if (User.objects.filter(username=user).exists() or User.objects.filter(email=user).exists()):
                return Response("Informações já cadastradas!", status=status.HTTP_400_BAD_REQUEST)
            novousuario = User.objects.create_user(username=user, password=senha, email=email, first_name=nome, last_name=sobrenome)
            novousuario.save()
            assign_role(novousuario, nivel_acesso)
            return Response(f"{nivel_acesso} cadastradado com sucesso!", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@permission_classes([IsAuthenticated])
class ListarSalas(APIView):
    def get(self, request, format= None):
        user_id = get_id_by_token(request)
        user = User.objects.get(id=user_id)
        if user is None:
            return Response("Você não tem permissão para acessar essa página!", status=status.HTTP_403_FORBIDDEN)
        salas = Sala.objects.all()
        serializer = SalaSerializer(salas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GerenciarReservas(APIView):
    def get(self, request, format=None):
        user_id = get_id_by_token(request)
        user = User.objects.get(id=user_id)
        if not (user.groups.filter(name='SuperAdmin').exists() or user.groups.filter(name='secretaria').exists()):
            return Response("Você não tem permissão para acessar essa página!", status=status.HTTP_403_FORBIDDEN)
        reservas = ReservaModel.objects.all()
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        user_id = get_id_by_token(request)
        user = User.objects.get(id=user_id)
        
        if not (user.groups.filter(name='SuperAdmin').exists() or user.groups.filter(name='secretaria').exists()):
            return Response("Você não tem permissão para acessar essa página!", status=status.HTTP_403_FORBIDDEN)
        else:
            serializer = GerenciarSerializer(data=request.data)
            if serializer.is_valid():
                reserva_id = serializer.validated_data["id"]
                reserva = ReservaModel.objects.get(id=reserva_id)
                delete_google_calendar_event(reserva.event_id,
                CalendarID= CALENDAR_IDS[reserva.sala.id - 1]
                )
                reserva.delete()
        return Response("Reserva excluída com sucesso!", status=status.HTTP_200_OK)
    


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
        user_id = get_id_by_token(request)
        user = User.objects.get(id=user_id)
        
        if not (user.groups.filter(name='SuperAdmin').exists() or user.groups.filter(name='secretaria').exists()):
            return Response("Você não tem permissão para acessar essa página!", status=status.HTTP_403_FORBIDDEN)
        try:
            reserva = ReservaModel.objects.get(id=id)
            sala_id = reserva.sala.id
        except ReservaModel.DoesNotExist:
            return Response("Reserva não encontrada!", status=status.HTTP_404_NOT_FOUND)
        serializer = ReservaSerializer(reserva, data=request.data)
        if serializer.is_valid():
            update_google_calendar_event(
                event_id=reserva.event_id,
                summary=f"Reserva de {reserva.responsavel} ",
                description=serializer.validated_data["descricao"],
                start_time=datetime.combine(serializer.validated_data["dia"], serializer.validated_data["hora_inicio"]),
                end_time=datetime.combine(serializer.validated_data["dia"], serializer.validated_data["hora_fim"]),
                CalendarID = CALENDAR_IDS[reserva.sala.id - 1]
            )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CadastrarSalas(APIView):
    def post(self, request, format=None):
        user_id = get_id_by_token(request)
        user = User.objects.get(id=user_id)
        
        if not (user.groups.filter(name='SuperAdmin').exists() or user.groups.filter(name='secretaria').exists()):
            return Response("Você não tem permissão para acessar essa página!", status=status.HTTP_403_FORBIDDEN)
        serializer = SalaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BuscaAgendamentos(APIView):
    def post(self, request, format=None):
        ar_condicionado = request.data.get("ar_condicionado", None)
        projetor = request.data.get("projetor", None)

        # Inicialmente, buscamos todas as reservas
        reservas_filtradas = ReservaModel.objects.all()

        # Em seguida, filtramos as salas com base nos valores de ar condicionado e projetor
        if ar_condicionado is not None:
            reservas_filtradas = reservas_filtradas.filter(sala__ar_condicionado=ar_condicionado)
        if projetor is not None:
            reservas_filtradas = reservas_filtradas.filter(sala__projetor=projetor)

        serializer = ReservaSerializer(reservas_filtradas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class BuscaFiltros(APIView):
    def post(self, request, format=None):
        ar_condicionado = request.data.get("ar_condicionado", None)
        projetor = request.data.get("projetor", None)

        # Inicialmente, buscamos todas as salas
        salas_filtradas = Sala.objects.all()

        # Em seguida, filtramos as salas com base nos valores de ar condicionado e projetor
        if ar_condicionado is not None:
            salas_filtradas = salas_filtradas.filter(ar_condicionado=ar_condicionado)
        if projetor is not None:
            salas_filtradas = salas_filtradas.filter(projetor=projetor)

        serializer = SalaSerializer(salas_filtradas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CalendarioID(APIView):
    def get(self, request, id, format=None):
        print (id)
        salanome = Sala.objects.get(id=id).nome
        calendario_id = CALENDAR_IDS[int(id -1)]
        if not salanome or not calendario_id:
            salanome = None
        data = {
            'salanome': salanome,
            'calendario_id': calendario_id,
        }
        return Response(data, status=status.HTTP_200_OK)