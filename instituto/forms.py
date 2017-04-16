from django import forms

class FechasForm(forms.Form):
    inicio = forms.DateField()
    fin = forms.DateField()