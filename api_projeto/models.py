from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class TipoUsuario(models.Model):#tipo de usuario criado
    user = models.OneToOneField(User, on_delete=models.CASCADE)#usuario só pode ter um tipo
    tipo = models.CharField(
        choices=[
            ('usuario', 'Usuário'),
            ('prestador', 'Prestador') #opções
        ]
    )
    
    def __str__(self):
        return self.user.username #retorna username

@receiver(post_save, sender=User)
def criar_perfil(sender, instance,created, **kwargs): #função para criar tipo automaticamente, garante q todo usuario tenha um tipo
    if created:
        TipoUsuario.objects.create(User= instance)

class Servico(models.Model):
    prestador = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50)
    descricao = models.TextField()
    duracao_minutos = models.IntegerField()
    preco = models.FloatField()
    ativo = models.BooleanField()