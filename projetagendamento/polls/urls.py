from django.urls import path
from . import views

urlpatterns = [
    path("salas/", views.Sala, name="salas"),
    path("agendar/", views.Agendar, name="agendar"),
    path("login/", views.Logar, name="login"),
    path("cadastro/", views.cadastro, name="cadastro"),
]
