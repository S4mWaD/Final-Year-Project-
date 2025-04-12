from django import template

register = template.Library()

@register.filter
def get_value(dict_obj, key):
    return dict_obj.get(key, 0)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)