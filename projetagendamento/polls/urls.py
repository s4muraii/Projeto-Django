from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("salas/", views.ListarSalas.as_view(), name="salas"),
    path("agendar/", views.ReservaView.as_view(), name="agendar"),
    path('login/', views.LoginView.as_view(), name='token_obtain_pair'),
    path('codigo/', views.VerifyCodeView.as_view(), name='codigo'),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("cadastro/", views.CadastroView.as_view(), name="cadastro"),
    path("gerenciar_reservas/", views.GerenciarReservas.as_view(), name="gerenciar_reservas"),
    path("editar_reserva/<int:id>/", views.EditarReservas.as_view(),name="editar_reserva"),
    path("cadastrar_sala/", views.CadastrarSalas.as_view(), name="cadastrar_sala"),
]