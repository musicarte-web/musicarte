from django.db import models
from django.contrib.auth.models import User

class Instrutor(models.Model):
    nome=models.CharField(max_length=120)
    especialidade=models.CharField(max_length=120, blank=True)
    telefone=models.CharField(max_length=30, blank=True)
    email=models.EmailField(blank=True)
    foto=models.ImageField(upload_to='instrutores/', blank=True, null=True)
    ativo=models.BooleanField(default=True)
    def __str__(self): return self.nome
    class Meta: ordering=['nome']

class Curso(models.Model):
    nome=models.CharField(max_length=120)
    descricao=models.TextField()
    carga_horaria=models.PositiveIntegerField(default=20, help_text='Em horas')
    instrutor=models.ForeignKey(Instrutor,on_delete=models.SET_NULL,null=True,blank=True,related_name='cursos')
    horario=models.CharField(max_length=120, blank=True)
    local=models.CharField(max_length=150, blank=True, default='IFPR - Campus Paranavaí')
    vagas=models.PositiveIntegerField(default=20)
    imagem=models.ImageField(upload_to='cursos/', blank=True, null=True)
    ativo=models.BooleanField(default=True)
    def __str__(self): return self.nome
    class Meta: ordering=['nome']

class Aluno(models.Model):
    usuario=models.OneToOneField(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='aluno')
    nome=models.CharField(max_length=120)
    idade=models.PositiveIntegerField(null=True,blank=True)
    telefone=models.CharField(max_length=30, blank=True)
    email=models.EmailField(blank=True)
    def __str__(self): return self.nome
    class Meta: ordering=['nome']

class Matricula(models.Model):
    STATUS=[('ATIVA','Ativa'),('CANCELADA','Cancelada')]
    aluno=models.ForeignKey(Aluno,on_delete=models.CASCADE,related_name='matriculas')
    curso=models.ForeignKey(Curso,on_delete=models.CASCADE,related_name='matriculas')
    data_matricula=models.DateField(auto_now_add=True)
    status=models.CharField(max_length=10,choices=STATUS,default='ATIVA')
    class Meta:
        ordering=['-data_matricula']
        constraints=[models.UniqueConstraint(fields=['aluno','curso'],name='matricula_unica')]
    def __str__(self): return f'{self.aluno} - {self.curso}'

class Aula(models.Model):
    curso=models.ForeignKey(Curso,on_delete=models.CASCADE,related_name='aulas')
    tema=models.CharField(max_length=180)
    data=models.DateField()
    observacoes=models.TextField(blank=True)
    def __str__(self): return f'{self.curso} - {self.data:%d/%m/%Y}'
    class Meta: ordering=['-data']

class Frequencia(models.Model):
    aula=models.ForeignKey(Aula,on_delete=models.CASCADE,related_name='frequencias')
    matricula=models.ForeignKey(Matricula,on_delete=models.CASCADE,related_name='frequencias')
    presente=models.BooleanField(default=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['aula','matricula'],name='frequencia_unica')]
    def __str__(self): return f'{self.matricula.aluno} - {self.aula} - {"Presente" if self.presente else "Ausente"}'

class Evento(models.Model):
    titulo=models.CharField(max_length=160)
    descricao=models.TextField()
    data=models.DateField()
    horario=models.TimeField(null=True,blank=True)
    local=models.CharField(max_length=180,blank=True)
    imagem=models.ImageField(upload_to='eventos/',blank=True,null=True)
    publicado=models.BooleanField(default=True)
    def __str__(self): return self.titulo
    class Meta: ordering=['data']

class Midia(models.Model):
    titulo=models.CharField(max_length=150)
    imagem=models.ImageField(upload_to='galeria/')
    legenda=models.CharField(max_length=240,blank=True)
    data=models.DateField(null=True,blank=True)
    publicada=models.BooleanField(default=True)
    def __str__(self): return self.titulo
    class Meta: ordering=['-data','-id']
