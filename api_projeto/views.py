from rest_framework.decorators import api_view
from .serializer import UserSerializer, ServicoSerializer, AgendamentoSerializer, DisponibilidadeHorarioSerializer
from .models import Servico, Prestador, Agendamentos, DisponibilidadedeHorario
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

class ServicoViewSet(ModelViewSet):
    queryset = Servico.objects.all()
    serializer_class = ServicoSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    def perform_create(self, serializer):
        prestador = Prestador.objects.get(user=self.request.user) #procura o prestador que pertene ao usuario logado
        serializer.save(prestador=prestador) #salva

class AgendamentoViewSet(ModelViewSet):
    queryset = Agendamentos.objects.all()
    serializer_class = AgendamentoSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user, status= "pendente")

class DisponibilidadedeHorarioViewSet(ModelViewSet):
    queryset= DisponibilidadedeHorario.objects.all()
    serializer_class = DisponibilidadeHorarioSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    def perform_create(self, serializer):
        prestador = Prestador.objects.get(user=self.request.user)
        serializer.save(prestador=prestador)

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
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def listagemCancelados(request):
    listaCancelada = Agendamentos.objects.filter(status='cancelado')
    serializer = AgendamentoSerializer(listaCancelada, many=True)

    return Response(serializer.data)