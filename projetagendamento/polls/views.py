from django.shortcuts import render, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from .models import ReservaModel, Sala
from .forms import VerificacaoDisponibilidadeForm, LoginForm, CadastroForm, ReservaForm


def superadmin_check(user):
    return user.is_superuser


def Agendar(request):
    if request.method == "POST":
        form = ReservaForm(request.POST)
        if form.is_valid():
            horarios_existentes = ReservaModel.objects.filter(
                sala=form.cleaned_data["sala"],
                data=form.cleaned_data["data"],
                hora_inicio__lt=form.cleaned_data["hora_fim"],
                hora_fim__gt=form.cleaned_data["hora_inicio"],
            )
            if horarios_existentes.exists():
                return HttpResponse("Horário indisponível!")
            else:
                reserva = form.save(commit=False)
                reserva.sala = form.cleaned_data["sala"]
                reserva.save()
                return HttpResponse("Reserva realizada com sucesso!")

    return render(request, "agendar.html", {"form": ReservaForm()})


def Logar(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            senha = form.cleaned_data["senha"]
            user = authenticate(request, username=username, password=senha)
            if user is not None:
                login(request, user)
                return HttpResponse("Login realizado com sucesso!")
            else:
                return HttpResponse("Login ou senha inválidos!")

        return render(request, "login.html", {"form": LoginForm()})

    else:
        form = LoginForm(request.POST)
    return render(request, "login.html", {"form": form})


@login_required
@user_passes_test(superadmin_check)
def cadastro(request):
    if request.method == "POST":
        form = CadastroForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Usuario cadastrada com sucesso!")
    else:
        form = CadastroForm()
    return render(request, "cadastro.html", {"form": form})
