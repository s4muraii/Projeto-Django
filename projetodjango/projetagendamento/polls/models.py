from django.db import models


# Create your models here.
Tipos_Sala = (
    ("REUNIÂO", "Sala de Reunião"),
    ("Laboratório", "Laboratório"),
    ("AUDITÓRIO", "Auditório"),
    ("SALA DE AULA", "Sala de Aula"),
    ("Oficina", "Oficina"),
)

class Sala(models.Model):
    nome = models.CharField(max_length=100)
    capacidade = models.IntegerField()
    tipo = models.CharField(max_length=15, choices=Tipos_Sala)
    projetor = models.BooleanField()
    ar_condicionado = models.BooleanField()
    disponivel = models.BooleanField()

    def __str__(self):
        return self.nome
    
class Reserva(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    responsavel = models.CharField(max_length=100)
    descricao = models.TextField()

    def __str__(self):
        return f"{self.sala} - {self.data} - {self.hora_inicio} - {self.hora_fim} - {self.responsavel}"