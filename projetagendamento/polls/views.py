from django.shortcuts import render, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect
from .models import ReservaModel, has_group, Sala
from .forms import LoginForm, CadastroForm, ReservaForm
from rolepermissions.roles import assign_role


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
def cadastro(request):
    if not (request.user.groups.filter(name='SuperAdmin').exists() or request.user.groups.filter(name='secretaria').exists()):
        return HttpResponse("Você não tem permissão para acessar essa página!")
    if request.method == "POST":
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["username"]
            senha = form.cleaned_data["senha"]
            if (User.objects.filter(username=user).exists() or User.objects.filter(email=user).exists()):
                return HttpResponse("Informações já cadastradas!")
            if request.user.groups.filter(name='SuperAdmin').exists():
                nivel_acesso = form.cleaned_data["nivel_acesso"]
                nivel_acesso = form.cleaned_data["nivel_acesso"]
                novousuario = User.objects.create_user(username=user, password=senha)
                novousuario.save()
                assign_role(novousuario, nivel_acesso)
            else:
                nivel_acesso = "funcionario"
                novousuario = User.objects.create_user(username=user, password=senha)
                novousuario.save()
                assign_role(novousuario, nivel_acesso)
            return HttpResponse(f"{nivel_acesso} cadastradado com sucesso!")
    elif request.user.groups.filter(name='SuperAdmin').exists():
            form = CadastroForm()
    else:
        form = CadastroForm()
        del form.fields['nivel_acesso']
    
    return render(request, "cadastro.html", {"form": form})

@login_required
def listasalas(request):
    salas = Sala.objects.all()
    return render(request, "salas.html", {"salas": salas})

def gerenciar_reservas(request):
    if not (request.user.groups.filter(name='SuperAdmin').exists() or request.user.groups.filter(name='secretaria').exists()):
        return redirect("salas")
    if request.method == "POST":
        reserva_id = request.POST.get("reserva_id")
        reserva = ReservaModel.objects.get(id=reserva_id)
        reserva.delete()
        return HttpResponse("Reserva excluída com sucesso!")
    else:
        reservas = ReservaModel.objects.all()
        return render(request, "gerenciar_reservas.html", {"reservas": reservas, "form": ReservaForm()})

@login_required
def editar_reservas(request, id):
    if not (request.user.groups.filter(name='SuperAdmin').exists() or request.user.groups.filter(name='secretaria').exists()):
        return redirect("salas")
    try:
        reserva = ReservaModel.objects.get(id=id)
    except ReservaModel.DoesNotExist:
        return HttpResponse("Reserva não encontrada!")

    if request.method == "POST":
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.save()
            return HttpResponse("Reserva editada com sucesso!")
    else:
        form = ReservaForm(instance=reserva)
        return render(request, "editar_reservas.html", {"form": form})