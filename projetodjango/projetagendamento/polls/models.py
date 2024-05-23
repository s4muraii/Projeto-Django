from django.db import models
import datetime

# Create your models here.
TIPOS_SALA = (
    ("REUNIÂO", "Sala de Reunião"),
    ("Laboratório", "Laboratório"),
    ("AUDITÓRIO", "Auditório"),
    ("SALA DE AULA", "Sala de Aula"),
    ("Oficina", "Oficina"),
)

class Sala(models.Model):
    nome = models.CharField(max_length=100)
    capacidade = models.IntegerField()
    tipo = models.CharField(max_length=15, choices=TIPOS_SALA)
    projetor = models.BooleanField()
    ar_condicionado = models.BooleanField()


    def __str__(self):
        return self.nome
    
    def horarios_disponiveis(self, data):
        reservas_no_dia = ReservaForm.objects.filter(sala=self, data=data)
        todos_horarios = [datetime.time(hour=i) for i in range(24)]  # considerando horários de 0 a 23 horas
        horarios_disponiveis = todos_horarios[:]

        for reserva in reservas_no_dia:
            for horario in todos_horarios:
                if reserva.hora_inicio <= horario < reserva.hora_fim:
                    horarios_disponiveis.remove(horario)

class ReservaForm(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, choices=TIPOS_SALA)
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    responsavel = models.CharField(max_length=100)
    descricao = models.TextField()

    def __str__(self):
        return f"{self.sala} - {self.data} - {self.hora_inicio} - {self.hora_fim} - {self.responsavel}"
    
    def verificar_disponibilidade(self):
            reservas_no_mesmo_horario = ReservaForm.objects.filter(
                sala=self.sala,
                data=self.data,
                hora_inicio__lt=self.hora_fim,
                hora_fim__gt=self.hora_inicio
            )
            return not reservas_no_mesmo_horario.exists()