from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from .models import *
from .forms import VerificacaoDisponibilidadeForm

def Agendar(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    elif request.method == "POST":
        form = ReservaForm(request.POST)
        if form.is_valid():
            sala = form.cleaned_data['sala']
            data = form.cleaned.data['data']
            horario = form.cleaned_data['horario']	


def verificar_disponibilidade(request):
    disponivel = None
    if request.method == 'POST':
        form = VerificacaoDisponibilidadeForm(request.POST)
        if form.is_valid():
            nome_item = form.cleaned_data['nome_item']
            try:
                item = Sala.objects.get(nome=nome_item)
                disponivel = item.disponivel
            except Sala.DoesNotExist:
                disponivel = False
    else:
        form = VerificacaoDisponibilidadeForm()
    return render(request, 'verificar_disponibilidade.html', {'form': form, 'disponivel': disponivel})

        