from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from .models import Venda, Produto, Cliente
from .forms import VendaForm, ItemVendaForm, ProdutoForm, ClienteForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Produto
from .serializers import ProdutoSerializer

# --- DASHBOARD / HISTÓRICO ---
@login_required
def historico_vendas(request):
    agora = timezone.now()
    filtro = request.GET.get('periodo', 'hoje')
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

# --- LANÇAMENTO DE VENDA (UNIFICADO) ---
@login_required
def lancar_venda(request):
    ultimo_cliente = None
    if request.method == 'POST':
        venda_form = VendaForm(request.POST)
        item_form = ItemVendaForm(request.POST)
        
        if venda_form.is_valid() and item_form.is_valid():
            venda = venda_form.save(commit=False)
            venda.usuario = request.user
            venda.save()
            
            item = item_form.save(commit=False)
            item.venda = venda
            item.preco_unitario = item.produto.preco_venda
            item.save()
            
            # --- LÓGICA DE CÁLCULO COM DESCONTO (SEGURA) ---
            subtotal = item.quantidade * item.preco_unitario
            # O uso de 'or 0' evita erro se o campo desconto for deixado em branco
            desconto = venda_form.cleaned_data.get('desconto') or 0
            tipo_desconto = venda_form.cleaned_data.get('tipo_desconto')

            if tipo_desconto == 'porcentagem':
                valor_desconto = subtotal * (desconto / 100)
            else:
                valor_desconto = desconto

            venda.total_venda = subtotal - valor_desconto
            venda.save()
            
            # --- FIDELIDADE ---
            ultimo_cliente = venda.cliente
            if ultimo_cliente:
                ultimo_cliente.compras_fidelidade += 1
                if ultimo_cliente.compras_fidelidade >= 20:
                    messages.success(request, f"🎉 PRÊMIO LIBERADO para {ultimo_cliente.nome}!")
                    ultimo_cliente.compras_fidelidade = 0
                else:
                    messages.success(request, f"Venda realizada! {ultimo_cliente.nome} agora tem {ultimo_cliente.compras_fidelidade} pontos.")
                ultimo_cliente.save()
            
            return redirect('lancar_venda')
    else:
        venda_form = VendaForm()
        item_form = ItemVendaForm()

    return render(request, 'lancar_venda.html', {
        'venda_form': venda_form,
        'item_form': item_form,
        'ultimo_cliente': ultimo_cliente
    })




# --- GESTÃO DE ESTOQUE E PRODUTOS ---
@login_required
def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_estoque')
    else:
        form = ProdutoForm()
    return render(request, 'cadastrar_produto.html', {'form': form})

@login_required
def lista_estoque(request):
    produtos = Produto.objects.all()
    return render(request, 'estoque.html', {'produtos': produtos})

@login_required
def atualizar_estoque(request, id):
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        nova_qtd = request.POST.get('quantidade')
        novo_preco = request.POST.get('preco') # Captura o novo preço

        if nova_qtd is not None:
            produto.estoque = int(nova_qtd)
        
        if novo_preco is not None:
            # Substitui vírgula por ponto para garantir que o Python entenda como decimal
            produto.preco_venda = novo_preco.replace(',', '.')
            
        produto.save()
        messages.success(request, f"Dados de {produto.nome} atualizados!")
    return redirect('lista_estoque')


@login_required
def deletar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    produto.delete()
    messages.success(request, f"Produto '{produto.nome}' removido!")
    return redirect('lista_estoque')

# --- CLIENTES E USUÁRIOS ---
@login_required
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente cadastrado com sucesso!")
            return redirect('cadastrar_cliente')
    else:
        form = ClienteForm()
    return render(request, 'cadastrar_cliente.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('historico_vendas')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def consulta_fidelidade(request):
    query = request.GET.get('q') # Para permitir busca por nome
    if query:
        clientes = Cliente.objects.filter(nome__icontains=query).order_by('nome')
    else:
        clientes = Cliente.objects.all().order_by('nome')
    
    # Adicionamos o cálculo de quanto falta diretamente na lista
    for cliente in clientes:
        cliente.faltam = 20 - cliente.compras_fidelidade
        
    return render(request, 'fidelidade.html', {'clientes': clientes, 'query': query})

@api_view(['GET'])
def api_lista_produtos(request):
    produtos = Produto.objects.all()
    serializer = ProdutoSerializer(produtos, many=True)
    return Response(serializer.data)