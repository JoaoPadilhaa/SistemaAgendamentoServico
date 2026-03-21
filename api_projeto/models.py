from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class TipoUsuario(models.Model):#tipo de usuario criado
    user = models.OneToOneField(User, on_delete=models.CASCADE)#usuario só pode ter um tipo
    tipo = models.CharField(
        choices=[
            ('cliente', 'Cliente'),
            ('prestador', 'Prestador') #opções
        ]
    )
    
    def __str__(self):
        return self.user.username #retorna username

@receiver(post_save, sender=User)
def criar_perfil(sender, instance,created, **kwargs): #função para criar tipo automaticamente, garante q todo usuario tenha um tipo
    if created:
        TipoUsuario.objects.create(User= instance)

class Prestador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)# tabela de prestador que esta ligada ao usario
    especialidade = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username

class Servico(models.Model):
    prestador = models.ForeignKey(Prestador, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50)
    descricao = models.TextField()
    duracao_minutos = models.IntegerField()
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    ativo = models.BooleanField()

    def __str__(self):
        return self.nome
    
class DisponibilidadedeHorario(models.Model):
    prestador = models.ForeignKey(Prestador, on_delete=models.CASCADE, related_name='disponibilidades')
    dia_semana = models.IntegerField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    
    def __str__(self):
        return f'{self.prestador} - Dia {self.dia_semana}'
    
class Agendamentos(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agendamentos')
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pendente', 'Pendente'),
            ('confirmado', 'Confirmado'),
            ('cancelado', 'Cancelado')
        ]
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cliente} - {self.servico}"
