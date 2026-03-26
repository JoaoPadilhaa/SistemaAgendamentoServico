from rest_framework import serializers
from django.contrib.auth.models import User, Group
from.models import Prestador, Servico, Agendamentos, DisponibilidadedeHorario, TipoUsuario


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    tipo = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id','username', 'password', 'tipo']
    
    def create(self, validated_data): #valida e cria o usuario
        tipo = validated_data.pop('tipo')
        user = User.objects.create_user(**validated_data)

        TipoUsuario.objects.create(user=user, tipo=tipo) # cria um tipousuario para o usuario
        
        if tipo.lower() == 'prestador':# verifica se o usuario é prestador, se for é adicionado na tabela prestador e no grupo prestador
            grupo, _ = Group.objects.get_or_create(name='Prestador')
            Prestador.objects.create(user=user, nome=user.username)
            user.groups.add(grupo)
        else:
            grupo, _ = Group.objects.get_or_create(name='Cliente')
            user.groups.add(grupo)
        return user
    
class ServicoSerializer(serializers.ModelSerializer):
    nomeprestador= serializers.SerializerMethodField()
    class Meta:
        model = Servico
        fields = ['nome', 'descricao', 'duracao_minutos', 'preco', 'ativo', 'nomeprestador']

    def get_nomeprestador(self, obj): # retorna o nome do prestador de serviço, pois o prestador esta diretamente ligado a servico
        return obj.prestador.nome


class PrestadorSerializer(serializers.ModelSerializer):
    servico = ServicoSerializer(many=True, read_only=True)
    class Meta:
        model = Prestador
        fields = '__all__'

class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model= Agendamentos
        fields = '__all__'

class DisponibilidadeHorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model= DisponibilidadedeHorario
        fields = '__all__'