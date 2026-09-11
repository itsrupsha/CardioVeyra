from django import template

register = template.Library()

@register.filter
def get_value(mapping, key):
    if mapping is None:
        return ""
    value = mapping.get(key, "")
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value
