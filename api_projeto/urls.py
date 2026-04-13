from django.urls import path, include
from .views import create
from rest_framework.routers import DefaultRouter
from .views import ServicoViewSet, AgendamentoViewSet, listagemCancelados, DisponibilidadedeHorarioViewSet
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'servicos', ServicoViewSet)
router.register(r'agendamentos', AgendamentoViewSet)
router.register(r'disponibilidade', DisponibilidadedeHorarioViewSet)

urlpatterns = [
    path('register/', create),
    path('login/', obtain_auth_token),
    path('', include (router.urls)),
    path('cancelados/', listagemCancelados)
]