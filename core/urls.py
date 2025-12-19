from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from vendas import views

urlpatterns = [
    # O segredo é deixar apenas admin.site.urls
    path('admin/', admin.site.urls),
    
    # Página inicial é o Login
    path('', auth_views.LoginView.as_view(template_name='index.html'), name='login'),
    
    # Rota para logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Rotas do seu sistema de vendas
    path('vendas/nova/', views.lancar_venda, name='lancar_venda'),
    path('historico/', views.historico_vendas, name='historico_vendas'),
    # Rotas de Estoque (As que estavam faltando os "names")
    path('estoque/', views.lista_estoque, name='lista_estoque'),
    path('estoque/novo/', views.cadastrar_produto, name='cadastrar_produto'),
    path('estoque/deletar/<int:id>/', views.deletar_produto, name='deletar_produto'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('estoque/atualizar/<int:id>/', views.atualizar_estoque, name='atualizar_estoque'),
    path('cliente/novo/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('fidelidade/', views.consulta_fidelidade, name='consulta_fidelidade'),
    path('api/produtos/', views.api_lista_produtos, name='api_produtos'),
]