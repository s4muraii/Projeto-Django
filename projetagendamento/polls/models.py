from django.db import models
import datetime
from django.contrib.auth.models import Group, Permission

# Create groups for each user level
group_superadmin = Group(name="SuperAdmin")
group_secretaria = Group(name="Secretaria")
group_professores = Group(name="Professor")

# Save the groups to the database
group_superadmin.save()
group_secretaria.save()
group_professores.save()

# Define permissions for each user level
permission_manage_users = Permission(
    name="Gerenciar Usuarios", codename="Gerenciar_Usuarios"
)
permission_add_user = Permission(name="Add User", codename="add_user")
permission_edit_user = Permission(name="Edit User", codename="edit_user")
permission_delete_user = Permission(name="Delete User", codename="delete_user")

# Assign permissions to groups
group_superadmin.permissions.add(
    permission_manage_users,
    permission_add_user,
    permission_edit_user,
    permission_delete_user,
)
group_secretaria.permissions.add(
    permission_manage_users, permission_add_user, permission_edit_user
)
group_professores.permissions.add()

# Create your models here.
TIPOS_SALA = (
    ("REUNIÂO", "Sala de Reunião"),
    ("Laboratório", "Laboratório"),
    ("AUDITÓRIO", "Auditório"),
    ("SALA DE AULA", "Sala de Aula"),
    ("OFICINA", "Oficina"),
)


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
