from django import forms

class FechasForm(forms.Form):
    inicio = forms.DateField()
    fin = forms.DateField()

class TestForm(forms.Form):
    nombre = forms.CharField(max_length=50)
    apellidos = forms.CharField(max_length=100)