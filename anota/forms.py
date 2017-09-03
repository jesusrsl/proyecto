# This Python file uses the following encoding: utf-8
import os, sys
from django import forms
from django.contrib.auth.forms import UserCreationForm
from models import ProfesorUser, Alumno, Asignatura
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Case, Count, When

class RegisterForm(UserCreationForm):

    class Meta:
        model = ProfesorUser
        fields = ['first_name', 'last_name', 'email', 'username']
        help_texts = {
            'username': 'Obligatorio. Hasta 150 caracteres. Solo letras, números y @/./+/-/_',
        }

#Formulario para la actualización de información personal
class UpdateForm(forms.ModelForm):
    class Meta:
        model = ProfesorUser
        fields = ['first_name', 'last_name', 'username', 'email']
        help_texts = {
            'username': 'Obligatorio. Hasta 150 caracteres. Solo letras, números y @/./+/-/_',
        }

    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['username'].widget.attrs['readonly'] = True

#Formulario para actualizar un ProfesorUser (por parte de un administrador)
class ProfesorUpdateForm(forms.ModelForm):
    class Meta:
        model = ProfesorUser
        fields = ['first_name', 'last_name', 'username', 'email', 'is_superuser']
        help_texts = {
            'username': 'Obligatorio. Hasta 150 caracteres. Solo letras, números y @/./+/-/_',
        }


class MatriculaForm(forms.Form):
    alumnos = forms.ModelMultipleChoiceField(queryset=Alumno.objects.all(),
                                          label=('Seleccionar alumnado'),
                                            required=True,
                                            widget=FilteredSelectMultiple(('Alumnos'),False,))

    asignaturas = forms.ModelMultipleChoiceField(queryset=Asignatura.objects.all(),
                                             label=('Seleccionar asignaturas'),
                                                 required=True,
                                                 widget=FilteredSelectMultiple(('Asignaturas'), False, ))

    def __init__(self, *args, **kwargs):
        qs=kwargs.pop('idGrupo')
        super(MatriculaForm, self).__init__(*args, **kwargs)
        if(int(qs) != 0):
            self.fields['alumnos'].queryset = Alumno.objects.filter(grupo_id=qs)
            self.fields['asignaturas'].queryset = Asignatura.objects.annotate(
                                importancia=Count(Case(When(grupo__id=qs, then=1)))
                                ).order_by('-importancia')
        else:
            self.fields['alumnos'].queryset = Alumno.objects.all()
            self.fields['asignaturas'].queryset = Asignatura.objects.all()

