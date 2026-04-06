from rest_framework import serializers
from django.contrib.auth.models import User, Group
from.models import Prestador, Servico, Agendamentos, DisponibilidadedeHorario, TipoUsuario
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    tipo = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True,
                                   validators=[UniqueValidator(queryset=User.objects.all(), message='Este email já está em uso!')])

    class Meta:
        model = User
        fields = ['id','username','email', 'password', 'tipo']
    
    def validate_email(self, value):
        email = value.lower()

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Este email já existe no sistema!')
        return email
    
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
    cliente = serializers.CharField(read_only=True)
    status = serializers.ChoiceField(choices=[
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ], required=False)

    class Meta:
        model= Agendamentos
        fields = ['cliente', 'servico', 'data_hora_inicio', 'data_hora_fim', 'status']

class DisponibilidadeHorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model= DisponibilidadedeHorario
        fields = '__all__'