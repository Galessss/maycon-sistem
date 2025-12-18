from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from .models import Venda, Produto
from .forms import ItemVendaForm, ProdutoForm

@login_required
def historico_vendas(request):
    agora = timezone.now()
    filtro = request.GET.get('periodo', 'hoje')  # Pega o filtro da URL, padrão é 'hoje'
    
    # Base da consulta
    vendas = Venda.objects.all()

    if filtro == 'semana':
        data_inicio = agora - timedelta(days=7)
        titulo = "Últimos 7 Dias"
    elif filtro == 'mes':
        data_inicio = agora - timedelta(days=30)
        titulo = "Últimos 30 Dias"
    else:
        data_inicio = agora.date()
        titulo = "Faturamento Hoje"

    # Filtra as vendas pelo período selecionado
    vendas_filtradas = vendas.filter(data_venda__gte=data_inicio)
    total_periodo = vendas_filtradas.aggregate(Sum('total_venda'))['total_venda__sum'] or 0
    qtd_periodo = vendas_filtradas.count()

    context = {
        'total': total_periodo,
        'quantidade': qtd_periodo,
        'titulo_filtro': titulo,
        'filtro_ativo': filtro,
        'vendas_recentes': vendas_filtradas.order_by('-data_venda')[:10]
    }
    
    return render(request, 'historico.html', context)

@login_required
def lancar_venda(request):
    if request.method == 'POST':
        form = ItemVendaForm(request.POST)
        if form.is_valid():
            nova_venda = Venda.objects.create(usuario=request.user)
            item = form.save(commit=False)
            item.venda = nova_venda
            item.preco_unitario = item.produto.preco_venda
            item.save()
            
            nova_venda.total_venda = item.quantidade * item.preco_unitario
            nova_venda.save()
            
            messages.success(request, "Venda realizada com sucesso!")
            return redirect('historico_vendas')
    else:
        form = ItemVendaForm()
    # REMOVIDO "vendas/" pois lancar_venda.html está na raiz de templates
    return render(request, 'lancar_venda.html', {'form': form})

@login_required
def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_estoque')
    else:
        form = ProdutoForm()
    # Pela imagem, o nome é dasboard.html ou cadastrar_produto.html? 
    # Ajuste para o nome exato do arquivo na pasta templates:
    return render(request, 'cadastrar_produto.html', {'form': form})

@login_required
def lista_estoque(request):
    produtos = Produto.objects.all()
    # Certifique-se de que existe um arquivo estoque.html em templates
    return render(request, 'estoque.html', {'produtos': produtos})