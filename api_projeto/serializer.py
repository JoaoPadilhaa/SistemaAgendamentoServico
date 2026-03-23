from rest_framework import serializers
from django.contrib.auth.models import User
from.models import Prestador, Servico, Agendamentos


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    tipo = serializers.CharField(write_only=True)

    class Meta:
        model:User
        fields = ['username', 'password', 'tipo']
    
    def create(self, validated_data):
        tipo = validated_data.pop('tipo')
        user = validated_data.create.user(**validated_data)

        user.tipousuario.tipo = tipo
        user.tipousuario.save()
        return user
    
class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model: Servico
        fields = '__all__'

class PrestadorSerializer(serializers.ModelSerializer):
    servico = ServicoSerializer(many=True, read_only=True)
    class Meta:
        model: Prestador
        fields = '__all__'

class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model: Agendamentos
        fields = '__all__'