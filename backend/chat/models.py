from django.db import models
import uuid

# Create your models here.

class PerfilUsuario(models.Model):
    """Perfil financeiro e profissional do usuário"""
    session_id    = models.UUIDField(default=uuid.uuid4, unique=True)
    #identificador unico da sessão
    cidade        = models.CharField(max_length=100, blank=True)
    area          = models.CharField(max_length=100, blank=True)
    cargo         = models.CharField(max_length=100, blank=True)
    salario_atual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    criado_em     = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil {self.session_id} - {self.cargo} em {self.cidade}"


class Conversa(models.Model):
    """Sessão de conversa do usuário"""
    perfil      = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='conversas')
    #liga a conversa a um perfil
    # on_delete=CASCADE se o perfil for deletado, as conversas tambem são
    #related_names = 'conversa' me permite fazer coisas do tipo: meu_perfil.conversas.all() mostra todas as conversa...../meu_perfil.conversas.filter(...) conversas filtradas.../ meu_perfil.conversas.count() lsitar quantidade de conversas.
    iniciada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversa {self.id} - {self.iniciada_em}"


class Mensagem(models.Model):
    """Mensagem individual dentro de uma conversa"""
    ROLES = [
        ('user', 'Usuário'),
        ('assistant', 'Agente'),
    #python('user', 'Usuário')
#  └─ o que salva    └─ o que mostra
#     no banco          pro humano
#O Django salva 'user' no banco, mas mostra 'Usuário' no admin e nos formulários. Economiza espaço no banco e ainda é legível pra humanos.
    ]

    conversa     = models.ForeignKey(Conversa, on_delete=models.CASCADE, related_name='mensagens')
    
    role         = models.CharField(max_length=10, choices=ROLES)
    
    conteudo     = models.TextField()
    
    intencao     = models.CharField(max_length=50, blank=True)
    
    dados_usados = models.JSONField(null=True, blank=True)
    ## Salva os dados do pandas que foram usados na análise
# Ex: {"salario_mediano": 7200, "custo_vida": 4800}
    criada_em    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.conteudo[:50]}"