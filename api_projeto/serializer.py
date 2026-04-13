from rest_framework import serializers
from django.contrib.auth.models import User, Group
from.models import Prestador, Servico, Agendamentos, DisponibilidadedeHorario, TipoUsuario
from rest_framework.validators import UniqueValidator
from datetime import timedelta


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    tipo = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True,
                                   validators=[UniqueValidator(queryset=User.objects.all(), message='Este email já está em uso!')])

    class Meta:
        model = User
        fields = ['id','username','email', 'password', 'tipo']
    
    #valida email unico
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
    nomeservico= serializers.SerializerMethodField()
    cliente = serializers.CharField(read_only=True)
    status = serializers.ChoiceField(choices=[
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ], required=False)
    servico = serializers.SlugRelatedField(
        queryset=Servico.objects.all(),
        slug_field='nome'
    )
    
    class Meta:
        model= Agendamentos
        fields = ['id','cliente', 'servico', 'data_hora_inicio', 'data_hora_fim', 'status', 'nomeservico']
        extra_kwargs = {
            'data_hora_fim' : {'read_only': True}
        }

    #retorna o nome do serviço
    def get_nomeservico(self, obj):
       return obj.servico.nome
    
    #Valida o agendamento por completo
    def validate(self, data):
        user = self.context['request'].user

        self.validar_permissioes_cliente(user, data)
        
       #pega a hora e servico ou em caso de patch, pega os valores que já estavam no banco
        inicio = data.get('data_hora_inicio', getattr(self.instance, 'data_hora_inicio', None))
        servico = data.get('servico', getattr(self.instance, 'servico', None))

        #calculo da hora do fim, só calcula se for enviado os dois acima
        if inicio and servico:
            fim_calculado = inicio + timedelta(minutes=servico.duracao_minutos)
            data['data_hora_fim'] = fim_calculado
        else:
            #se não for enviado, pega o fim que já estava no banco
            fim_calculado = getattr(self.instance, 'data_hora_fim', None)

        if fim_calculado:
            if inicio > fim_calculado:
                raise serializers.ValidationError('Erro: A hora de início deve ser anterior a hora de fim!')

            prestador_id = servico.prestador.id

            #valida se são horários permitidos ao marcar
            agendamentos = Agendamentos.objects.filter(
                servico__prestador_id=prestador_id,
                data_hora_inicio__lt=fim_calculado,
                data_hora_fim__gt=inicio)
            
            if self.instance:
                agendamentos = agendamentos.exclude(pk=self.instance.pk)
            if agendamentos.exists():
                raise serializers.ValidationError('Conflito de horário')
        
        return data
    
    #Função de ver se o usuario é cliente
    def validar_permissioes_cliente(self, user, data):
        is_cliente = user.groups.filter(name='Cliente').exists()
        if self.instance and is_cliente:
            #pega o status do agendamento e pga o status novo
            status_novo = data.get('status')
            status_atual = self.instance.status

            #verifica se o status novo é algo diferente de cancelado
            if status_novo and status_novo != 'cancelado':
                raise serializers.ValidationError('Clientes só podem alterar o status para Cancelado')
            #verifica se o status não é pendente, se não for avisa que só pode alterar pendente para cancelado
            if status_atual != 'pendente':
                raise serializers.ValidationError('Apenas agendamenteos pendentes podem ser cancelados')
            if 'data_hora_inicio' in data and data['data_hora_inicio'] != self.instance.data_hora_inicio:
                raise serializers.ValidationError('Clientes não podem alterar o horário do agendamento.')
            

class DisponibilidadeHorarioSerializer(serializers.ModelSerializer):
    nomeprestador = serializers.SerializerMethodField()
    class Meta:
        model= DisponibilidadedeHorario
        fields = ['nomeprestador','dia_semana', 'hora_inicio', 'hora_fim']

    def get_nomeprestador(self, obj):
        return obj.prestador.nome

