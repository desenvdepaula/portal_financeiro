from django.db import models
    
class ClassificacaoServicos(models.Model):
    classificacao = models.CharField(max_length=255)
