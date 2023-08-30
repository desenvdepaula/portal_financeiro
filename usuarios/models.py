from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

def get_file_path(instance, filename):
    filename = f'foto_perfil/{instance.username}/{filename}'
    return filename

class UsuarioManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser',False)
        extra_fields.setdefault('is_staff',False)
        return self._create_user(email, password, **extra_fields) 

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('O status de super usuário deve ser definido.')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('O status de mebro da equipe deve ser definido.')

        return self.create_user(email,  password, **extra_fields)
            
class Usuario(AbstractUser):
    foto = models.ImageField("Foto",upload_to=get_file_path, blank=True)
    
    departamento = models.CharField("Departamento",max_length = 255, blank=True, null=True)
    cd_tareffa = models.CharField("Código Tareffa",max_length = 10, blank=True, null=True)
    cd_questor = models.CharField("Código Questor",max_length = 10, blank=True, null=True)
    cd_folha = models.CharField("Folha",max_length = 10, blank=True, null=True)
    date_aniversario = models.DateField(blank=True, null=True)
    
    _default_manager = 'pid_db'

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name','last_name','email']

    def __str__(self):
        return self.email

    objects = UsuarioManager()
    objects = objects.db_manager('pid_db')

    class Meta:
        permissions = [
            ('importar_duplicatas', "Pode importar duplicatas")
        ]
