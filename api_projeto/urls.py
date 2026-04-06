from django.urls import path, include
from .views import create
from rest_framework.routers import DefaultRouter
from .views import ServicoViewSet, AgendamentoViewSet
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'servicos', ServicoViewSet)
router.register(r'agendamentos', AgendamentoViewSet)

urlpatterns = [
    path('register/', create),
    path('login/', obtain_auth_token),
    path('', include (router.urls)),
]