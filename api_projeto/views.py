from rest_framework.decorators import api_view
from rest_framework import status
from .serializer import UserSerializer, ServicoSerializer
from .models import Servico, Prestador
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

class ServicoViewSet(ModelViewSet):
    queryset = Servico.objects.all()
    serializer_class = ServicoSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    def perform_create(self, serializer):
        prestador = Prestador.objects.get(user=self.request.user) #procura o prestador que pertene ao usuario logado
        serializer.save(prestador=prestador) #salva

@api_view(['POST'])
def create(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "user": serializer.data,
            "token": token.key
        })
    return Response(serializer.errors)

