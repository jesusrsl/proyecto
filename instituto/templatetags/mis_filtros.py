from django import template
from django.template import loader, Node, Variable
from django.utils.encoding import smart_str, smart_unicode
from django.template.defaulttags import url
from django.template import VariableDoesNotExist

register = template.Library()

@register.filter(name='veces')
def veces(number):
    if number is None:
        return range(0)
    else:
        return range(number)

@register.assignment_tag
def define(val=None):
  return val

@register.filter(name='addcss')
def addcss(field, css):
   return field.as_widget(attrs={"class":css})

@register.filter(name='addplaceholder')
def addplaceholder(field, placeholder):
   return field.as_widget(attrs={'class':"form-control",'placeholder':placeholder})


