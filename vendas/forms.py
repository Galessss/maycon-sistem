from django import forms
from .models import Venda, ItemVenda, Produto, Cliente

class VendaForm(forms.ModelForm):
    tipo_desconto = forms.ChoiceField(
        choices=[('valor', 'R$'), ('porcentagem', '%')],
        initial='valor',
        required=False # Campo Opcional
    )
    desconto = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        initial=0, 
        required=False, # Campo Opcional
        widget=forms.NumberInput(attrs={'placeholder': '0.00'})
    )

    class Meta:
        model = Venda
        fields = ['cliente', 'tipo_desconto', 'desconto']

    # Ajuste para que os preços apareçam no HTML
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se você quiser injetar preços no select de produtos via ItemVendaForm, 
        # faremos isso no template para ser mais direto.
        
class ItemVendaForm(forms.ModelForm):
    class Meta:
        model = ItemVenda
        fields = ['produto', 'quantidade']

    def clean_quantidade(self):
       
        quantidade = self.cleaned_data.get('quantidade')
        produto = self.cleaned_data.get('produto')
        if produto and produto.estoque < quantidade:
            raise forms.ValidationError(f"Estoque insuficiente! Disponível: {produto.estoque}")
        return quantidade

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'preco_venda', 'estoque']
        

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo do cliente'}),
        }
        
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome']