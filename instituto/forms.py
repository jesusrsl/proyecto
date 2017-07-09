# This Python file uses the following encoding: utf-8
import os, sys
from django import forms
from django.contrib.auth.forms import UserCreationForm
from models import ProfesorUser

class RegisterForm(UserCreationForm):

    class Meta:
        model = ProfesorUser
        fields = ['first_name', 'last_name', 'email', 'username']
        help_texts = {
            'username': 'Obligatorio. Hasta 150 caracteres. Solo letras, números y @/./+/-/_',
        }

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

"""
class FechasForm(forms.Form):
    inicio = forms.DateField()
    fin = forms.DateField()

class TestForm(forms.Form):
    nombre = forms.CharField(max_length=50)
    apellidos = forms.CharField(max_length=100)

"""