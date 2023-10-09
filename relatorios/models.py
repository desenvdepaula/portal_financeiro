from django.db import models
    
class ClassificacaoServicos(models.Model):
    classificacao = models.CharField(max_length=255)
    
class ClassificacaoFaturamentoServicos(models.Model):
    codigo = models.CharField(primary_key=True, max_length=8)
    descricao = models.CharField(max_length=255)
    classificacao = models.ForeignKey(ClassificacaoServicos, on_delete=models.CASCADE)