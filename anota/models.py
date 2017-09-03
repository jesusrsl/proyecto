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
        self._meta.get_field('username').help_text ='Obligatorio. Hasta 150 caracteres. Solo letras, números y @/./+/-/_'

        for v in self._meta.get_field('username').validators:
            v.message = 'Introduzca un nombre de usuario válido. Solo debe contener letras, números y los caracteres @/./+/-/_'

        self._meta.get_field('username').verbose_name = 'usuario'
        self._meta.get_field('password').verbose_name = 'contraseña'
        self._meta.get_field('first_name').verbose_name = 'nombre'
        self._meta.get_field('last_name').verbose_name = 'apellidos'

    def __unicode__(self):
        return self.first_name + " " + self.last_name

    def get_absolute_url(self):
        return reverse('lista-profesores')

    class Meta:
        ordering = ['last_name','first_name']

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
        (1, '1º ESO'),
        (2, '2º ESO'),
        (3, '3º ESO'),
        (4, '4º ESO'),
        (5, '1º BACH'),
        (6, '2º BACH'),
        (7, '1º CFGM'),
        (8, '2º CFGM'),
        (9, '1º CFGS'),
        (10, '2º CFGS'),
        (11, 'otros'),
    )
    curso = models.PositiveSmallIntegerField(choices=CURSO_CHOICES)
    unidad = models.CharField(max_length=10)
    tutor = models.OneToOneField(ProfesorUser, on_delete=models.PROTECT)    #clave alterna
    distribucion = models.PositiveSmallIntegerField(default=6, validators=[MaxValueValidator(8), MinValueValidator(1)])

    def __unicode__(self):
        return "%s %s" % (self.get_curso_display(), self.unidad)

    #def __str__(self):
    #    return unicode(self).encode('utf-8')

    def get_absolute_url(self):
        return reverse('lista-grupos')

    def ordenar_alumnos(self):
        return self.alumno_set.order_by('orden')

    class Meta:
        ordering = ['curso', 'unidad']
        verbose_name_plural = 'grupos'
        unique_together = ('curso', 'unidad',)


class Asignatura(models.Model):
    nombre = models.CharField(max_length=50)
    profesor = models.ForeignKey(ProfesorUser, on_delete=models.PROTECT)
    grupo = models.ForeignKey(Grupo, on_delete=models.PROTECT)
    distribucion = models.PositiveSmallIntegerField(default=6, validators=[MaxValueValidator(8), MinValueValidator(1)])

    def __unicode__(self):
        return "%s %s %s" % (
            self.nombre,  self.grupo.get_curso_display(),
            self.grupo.unidad)

    #def __str__(self):
    #    return unicode(self).encode('utf-8')


    def get_absolute_url(self):
        return reverse('lista-asignaturas')

    def ordenar_alumnos(self):
        return self.alumno_set.order_by('matricula__orden')

    class Meta:
        ordering = ['grupo','nombre','profesor']
        verbose_name_plural = 'asignaturas'
        unique_together = ('nombre', 'grupo',)


class Alumno(models.Model):
    nombre = models.CharField(max_length=50)
    apellido1 = models.CharField(max_length=50)
    apellido2 = models.CharField(max_length=50, blank=True)
    fecha_nacimiento = models.DateField()
    email = models.EmailField(null=True, blank=True)
    foto = models.ImageField(upload_to='fotografias/', blank=True)
    grupo = models.ForeignKey(Grupo, on_delete=models.PROTECT)
    orden = models.PositiveIntegerField(default=0)
    asignaturas = models.ManyToManyField(Asignatura, through='Matricula')

    def __init__(self, *args, **kwargs):
        super(Alumno, self).__init__(*args, **kwargs)

        self._meta.get_field('apellido1').verbose_name = 'primer apellido'
        self._meta.get_field('apellido2').verbose_name = 'segundo apellido'
        self._meta.get_field('fecha_nacimiento').verbose_name = 'fecha de nacimiento'

    def __unicode__(self):
        return "%s %s %s" % (self.nombre, self.apellido1, self.apellido2)

    #def __str__(self):
    #    return unicode(self).encode('utf-8')

    def get_absolute_url(self):
        #return reverse('lista-alumnos')
        #otra opción -->
        return reverse('detalle-alumno', kwargs={'pk': self.id})

    def save(self):

        #se calcula el orden
        if self.orden == 0:
            max = 0
            for m in Alumno.objects.filter(grupo=self.grupo):
                if max <= m.orden:
                    max = m.orden
            self.orden = max + 1

        try:
            this = Alumno.objects.get(id=self.id)
            if this.foto == self.foto:
                self.foto = this.foto
            else:
                this.foto.delete(save=False)
        except:
            pass  # when new photo then we do nothing, normal case

        super(Alumno, self).save()
        if self.foto:
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
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
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
        unique_together = ('alumno', 'asignatura',)

class Anotacion(models.Model):
    FALTA_CHOICES = (
        ('', '----'),
        ('I', 'Injustificada'),
        ('J', 'Justificada'),
        ('R', 'Retraso'),
    )

    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    fecha = models.DateField(default=date.today)
    falta = models.CharField(max_length=1, choices=FALTA_CHOICES, null=True, blank=True)
    #falta = models.BooleanField(default=False)
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
        unique_together = ('alumno', 'asignatura', 'fecha')
