# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from datetime import date, datetime

from PIL import Image

# Create your models here.

class ProfesorUser(User):
    #username, password, email, first_name, last_name

    def __init__(self, *args, **kwargs):
        super(ProfesorUser, self).__init__(*args, **kwargs)
        self._meta.get_field('username').verbose_name = 'usuario'
        self._meta.get_field('password').verbose_name = 'contraseña'
        self._meta.get_field('first_name').verbose_name = 'nombre'
        self._meta.get_field('last_name').verbose_name = 'apellidos'

    def __unicode__(self):
        return self.first_name + " " + self.last_name + " (" + self.username + ")"

    def get_absolute_url(self):
        return reverse('lista-profesores')

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name_plural = 'profesores'

"""
class ProfesorUser(models.Model):
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s %s" % (self.nombre, self.apellidos)

    #def __str__(self):
    #    return unicode(self).encode('utf-8')

    def get_absolute_url(self):
        return reverse('lista-profesores')

    class Meta:
        ordering = ['apellidos', 'nombre']
        verbose_name_plural = 'profesores'
"""
"""
class Aula(models.Model):
    planta = models.PositiveSmallIntegerField()
    pasillo = models.CharField(max_length=20, blank = True)
    numero = models.PositiveIntegerField()
    filas = models.PositiveIntegerField()
    columnas = models.PositiveIntegerField()

    def __unicode__(self):
        return "Planta %d, pasillo %s, número %d" % (self.planta, self.pasillo, self.numero)

    #def __str__(self):
    #    return unicode(self).encode('utf-8')

    def get_absolute_url(self):
        return reverse('lista-aulas')

    class Meta:
        ordering = ['planta', 'pasillo', 'numero']
        verbose_name_plural = 'aulas'
"""

class Grupo(models.Model):
    CURSO_CHOICES = (
        (0, '1º ESO'),
        (1, '2º ESO'),
        (2, '3º ESO'),
        (3, '4º ESO'),
        (4, '1º BACH'),
        (5, '2º BACH'),
        (6, '1º CFGM'),
        (7, '2º CFGM'),
        (8, '1º CFGS'),
        (9, '2º CFGS'),
        (10, 'otros'),
    )
    curso = models.PositiveSmallIntegerField(choices=CURSO_CHOICES)
    unidad = models.CharField(max_length=10, blank=True)
    tutor = models.ForeignKey(ProfesorUser, on_delete=models.PROTECT)

    def __unicode__(self):
        return "%s %s" % (self.get_curso_display(), self.unidad)

    #def __str__(self):
    #    return unicode(self).encode('utf-8')

    def get_absolute_url(self):
        return reverse('lista-grupos')

    class Meta:
        ordering = ['curso', 'unidad']
        verbose_name_plural = 'grupos'


class Asignatura(models.Model):
    nombre = models.CharField(max_length=50)
    profesor = models.ForeignKey(ProfesorUser, on_delete=models.PROTECT)
    #profesor = models.ForeignKey(User, on_delete=models.PROTECT)
    grupo = models.ForeignKey(Grupo, on_delete=models.PROTECT)
    distribucion = models.PositiveSmallIntegerField(default=6, validators=[MaxValueValidator(8), MinValueValidator(1)])

    def __unicode__(self):
        return "%s %s %s %s %s" % (
            self.nombre, self.profesor.first_name, self.profesor.last_name, self.grupo.get_curso_display(),
            self.grupo.unidad)

    #def __str__(self):
    #    return unicode(self).encode('utf-8')


    def get_absolute_url(self):
        return reverse('lista-asignaturas')

    class Meta:
        ordering = ['grupo','nombre','profesor']
        verbose_name_plural = 'asignaturas'


class Alumno(models.Model):
    nombre = models.CharField(max_length=50)
    apellido1 = models.CharField(max_length=50)
    apellido2 = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField()
    email = models.EmailField(null=True, blank=True)
    foto = models.ImageField(upload_to='fotografias/', blank=True)
    grupo = models.ForeignKey(Grupo, on_delete=models.PROTECT)
    asignaturas = models.ManyToManyField(Asignatura, through='Matricula')
    #asignaturas = models.ManyToManyField(Asignatura, limit_choices_to = {'grupo':grupo})

    def __unicode__(self):
        return "%s %s %s" % (self.nombre, self.apellido1, self.apellido2)

    #def __str__(self):
    #    return unicode(self).encode('utf-8')

    def get_absolute_url(self):
        return reverse('lista-alumnos')
        #otra opción -->
        # return reverse('detalle-alumno', kwargs={'pk': self.id})

    def save(self):

        super(Alumno, self).save()

        if self.foto != "":
            image = Image.open(self.foto)

            size = (200, 200)
            image = image.resize(size, Image.ANTIALIAS)
            image.save(self.foto.path)

    class Meta:
        ordering = ['apellido1', 'apellido2', 'nombre']
        verbose_name_plural = 'alumnos'

@receiver(post_delete, sender=Alumno)
def foto_delete(sender, instance, **kwargs):
    # Borra los ficheros de las fotos de los alumnos que se eliminan.
    instance.foto.delete(False)

class Matricula(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.PROTECT)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.PROTECT)
    orden = models.PositiveIntegerField(default=0)

    def save(self):
        if self.orden == 0:
            max = 0
            for m in Matricula.objects.filter(asignatura=self.asignatura):
                if max <= m.orden:
                    max = m.orden
            self.orden = max + 1

        #se guarda el objeto
        super(Matricula, self).save()  # Call the "real" save() method."""

    def __unicode__(self):
        return "%s %s %s matriculado en %s" % (self.alumno.nombre, self.alumno.apellido1, self.alumno.apellido2, self.asignatura.nombre)

    def get_absolute_url(self):
        return reverse('lista-matriculas')

    class Meta:
        ordering = ['asignatura','orden']
        verbose_name_plural = 'matriculas'

class Anotacion(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    fecha = models.DateField(default=date.today)
    falta = models.BooleanField(default=False)
    trabaja = models.BooleanField(default=False)
    positivos = models.PositiveIntegerField(null=True, blank=True)
    negativos = models.PositiveIntegerField(null=True, blank=True)


    def __unicode__(self):
        return "Anotación de %s %s %s en %s, el %s" % (self.alumno.nombre, self.alumno.apellido1, self.alumno.apellido2, self.asignatura.nombre, unicode(self.fecha))

    def get_absolute_url(self):
        """if self.fecha == date.today():
            return reverse('detalle-asignatura', kwargs={'pk': self.asignatura.id})
        else:"""


        return reverse('detalle-asignatura-cuad', kwargs={'pk': self.asignatura.id, 'fecha': datetime.strftime(self.fecha, '%d/%m/%Y')})
        #return reverse('lista-alumnos')


    class Meta:
        ordering = ['asignatura','fecha', 'alumno']
        verbose_name_plural = 'anotaciones'
