from django.urls import path
from . import views

urlpatterns = [
    path("salas/", views.listasalas, name="salas"),
    path("agendar/", views.Agendar, name="agendar"),
    path("login/", views.Logar, name="login"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("gerenciar_reservas/", views.gerenciar_reservas, name="gerenciar_reservas"),
    path("editar_reserva/<int:id>/", views.editar_reservas, name="editar_reserva"),
    path("cadastrar_sala/", views.cadastrar_sala, name="cadastrar_sala"),
]
