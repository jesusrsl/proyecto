from django import template

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