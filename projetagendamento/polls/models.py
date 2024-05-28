from django.db import models

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

def has_group(self, group_name):
    return self.groups.filter(name=group_name).exists()

class Sala(models.Model):
    nome = models.CharField(max_length=100)
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
