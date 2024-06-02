from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import AbstractUser
import platform
import requests
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from rest_framework_simplejwt.state import token_backend
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

def create_google_calendar_event(summary, description, start_time, end_time, CalendarID):
    # Caminho para o arquivo de credenciais da conta de serviço
    calendar_id = CalendarID[1]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    service_account_file = os.path.join(current_dir, '../configs/service_account.json')

    # Carregar as credenciais da conta de serviço
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=['https://www.googleapis.com/auth/calendar'])

    # Construir o serviço do Google Calendar
    service = build('calendar', 'v3', credentials=credentials)

    # Criar o evento
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
    }

    # Enviar o evento para o Google Calendar
    event = service.events().insert(calendarId=calendar_id, body=event).execute()

    return event
def update_google_calendar_event(event_id, summary, description, start_time, end_time, CalendarID):
    calendar_id = CalendarID[1]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    service_account_file = os.path.join(current_dir, '../configs/service_account.json')

    # Carregar as credenciais da conta de serviço
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=credentials)
    # atualiza o evento
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    event['summary'] = summary
    event['description'] = description
    event['start']['dateTime'] = start_time.isoformat()
    event['end']['dateTime'] = end_time.isoformat()
    updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()

    return updated_event

def delete_google_calendar_event(event_id, CalendarID):    
    calendar_id = CalendarID[1]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    service_account_file = os.path.join(current_dir, '../configs/service_account.json')

    # Carregar as credenciais da conta de serviço
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=credentials)

    # Deletar o evento
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    
    
CALENDAR_IDS = (
    ("1", "90ac40b338980cf78cbeacae0393f1ca2e4a4f2042bc6b8d80c475b48adff1ec@group.calendar.google.com"),
    ("2", "8a54031d366eca74dc9dd8b47c6191b9e98e4cb26bc6fc7a4e3572b36798f0ed@group.calendar.google.com"),
    ("3", "faecd5fc816d03ad495c42dc830e1ef1e97470d35db0ce22ed934ef75271fcce@group.calendar.google.com"),
    ("4", "de16f2d1817ace50376cefdd80022b130e503ecf11a3a23e56d0407d4b9bce57@group.calendar.google.com"),
    ("5", "1329a39162eff594300683899ba196ed3cb54d7a104b3154251ecadb79683b3e@group.calendar.google.com"),
    ("6", "e30eaeafd10c2a71110ebf7349d58563e3af2602211c99104c0bf9c54596153b@group.calendar.google.com"),
    ("7", "1f477876c8f37030c4068afa25d4a83f2d0e324a3465cf8bbf79d5fccc833f18@group.calendar.google.com"),
    ("8", "d12a5f8feec2294f8119b5762e404860f42b64f332dddc7fc83919b302719e1e@group.calendar.google.com"),
    ("9", "e6f29b89afce7bf960fbf6728625993422d9848293beb04fd3ae2b1b70a3964e@group.calendar.google.com"),
    ("10", "5b81ff291d04d03f1c7b12ce116e89e6f1c6a234a23ea1690bc9af57a972cb68@group.calendar.google.com"),
    
)
TIPOS_SALA = (
    ("REUNIÂO", "Sala de Reunião"),
    ("Laboratório", "Laboratório"),
    ("AUDITÓRIO", "Auditório"),
    ("SALA DE AULA", "Sala de Aula"),
    ("OFICINA", "Oficina"),
)

NIVEL_ACESSO = (
    ("secretaria", "Secretaria"),
    ("funcionario", "Funcionario"),
)

def get_id_by_token(request):
    token = request.headers.get('Authorization').split(' ')[1]
    print ("Token: ", token)
    token_bytes = token.encode('utf-8')  # Convert the token to bytes
    valid_token = token_backend.decode(token_bytes, verify=False)
    id = valid_token['user_id']
    return id

def send_verification_email(user, verification_code):
    # Get system information
    system_info = platform.uname()

    # Get IP information
    ip_info = requests.get('https://ipinfo.io').json()
    email_body = f"""
        <div style="padding: 30px; text-align: center;">
            <h1 style="color: blue; font-size: 24px;">Codigo De Verificação</h1>
            <p">Olá! <span style="font-weight: bold;">{user}</span></p>
            <p style="font-size: 18px;">Seu código de verificação é:</p>
            <br>
            <h2 style="color: green; font-size: 24px; background-color: #f2f2f2; margin: 20px;">{verification_code}</h2>
            <p style="font-size: 16px; text-align: left;">Informações de login:</p>
            <ul style="text-align: left;">
                <li>Sistema Operacional: {system_info.system}</li>
                <li>Endereço IP: {ip_info['ip']}</li>
                <li>Localização: {ip_info['city']}, {ip_info['region']}</li>
                
            </ul>
        </div>
        """

    # Create a plain-text version of the email body
    text_email_body = f"""
        Seu código de verificação

        Seu código de verificação é {verification_code}

        Aqui estão algumas informações adicionais:

        Sistema operacional: {system_info.system}
        Endereço IP: {ip_info['ip']}
        Localização: {ip_info['city']}, {ip_info['region']}
        """

    # Send the email
    send_mail(
        'Seu Codigo De Verificação',
        text_email_body,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
        html_message=email_body,
    )

class Sala(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    capacidade = models.IntegerField()
    tipo = models.CharField(max_length=15, choices=TIPOS_SALA)
    projetor = models.BooleanField()
    ar_condicionado = models.BooleanField()
    id = models.AutoField(primary_key=True)
    imagem = models.ImageField(upload_to='imagens/', null=True, blank=True)

    def __str__(self):
        return self.nome
    


class ReservaModel(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    dia = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    responsavel = models.CharField(max_length=100)
    descricao = models.TextField()
    event_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.sala} - {self.dia} - {self.hora_inicio} - {self.hora_fim} - {self.responsavel}"

    def verificar_disponibilidade(self):
        reservas_no_mesmo_horario = ReservaModel.objects.filter(
            sala=self.sala,
            data=self.data,
            hora_inicio__lt=self.hora_fim,
            hora_fim__gt=self.hora_inicio,
        )
        return not reservas_no_mesmo_horario.exists()


class User(AbstractUser):
    nivel_acesso = models.CharField(max_length=15, choices=NIVEL_ACESSO, default="funcionario")
    
    groups = models.ManyToManyField(Group, blank=True, related_name="polls_user_set")
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name="polls_user_set")