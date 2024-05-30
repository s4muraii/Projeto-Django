from email.mime.text import MIMEText
from django.core.mail import send_mail
from django.db import models
import platform
import requests
from django.conf import settings

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

    def __str__(self):
        return self.nome
    


class ReservaModel(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    responsavel = models.CharField(max_length=100)
    descricao = models.TextField()

    def __str__(self):
        return f"{self.sala} - {self.data} - {self.hora_inicio} - {self.hora_fim} - {self.responsavel}"

    def verificar_disponibilidade(self):
        reservas_no_mesmo_horario = ReservaModel.objects.filter(
            sala=self.sala,
            data=self.data,
            hora_inicio__lt=self.hora_fim,
            hora_fim__gt=self.hora_inicio,
        )
        return not reservas_no_mesmo_horario.exists()

