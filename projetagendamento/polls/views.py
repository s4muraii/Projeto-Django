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


def verificar_disponibilidade(request):
    disponivel = None
    if request.method == "POST":
        form = VerificacaoDisponibilidadeForm(request.POST)
        if form.is_valid():
            nome_item = form.cleaned_data["nome_item"]
            try:
                item = Sala.objects.get(nome=nome_item)
                disponivel = item.disponivel
            except Sala.DoesNotExist:
                disponivel = False
    else:
        form = VerificacaoDisponibilidadeForm()
    return render(
        request, "disponibilidade.html", {"form": form, "disponivel": disponivel}
    )


def Login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            senha = form.cleaned_data["senha"]
            user = authenticate(username=username, password=senha)
            if user is not None:
                login(request, user)
                return HttpResponse("Login realizado com sucesso!")
            else:
                return HttpResponse("Login ou senha inválidos!")

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
            return HttpResponse("Sala cadastrada com sucesso!")
    else:
        form = CadastroForm()
    return render(request, "cadastro.html", {"form": form})
