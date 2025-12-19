from rest_framework import serializers
from .models import Produto, Cliente

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id', 'nome', 'preco_venda', 'estoque']