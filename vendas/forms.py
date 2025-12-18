from django import forms
from .models import Venda, ItemVenda, Produto

# Formulário para realizar a venda
class ItemVendaForm(forms.ModelForm):
    class Meta:
        model = ItemVenda
        fields = ['produto', 'quantidade']

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        produto = self.cleaned_data.get('produto')
        
        if produto.estoque < quantidade:
            raise forms.ValidationError(f"Estoque insuficiente! Disponível: {produto.estoque}")
        return quantidade

# Formulário para cadastrar novos produtos (O que estava faltando!)
class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'preco_venda', 'estoque']