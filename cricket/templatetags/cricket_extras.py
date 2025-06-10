from django import template

register = template.Library()

@register.filter(name='split_string')
def split_string(value, delimiter=','):
    """Split a string into a list using the specified delimiter"""
    return [x.strip() for x in value.split(delimiter)]
