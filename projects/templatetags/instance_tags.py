from django import template

register = template.Library()

@register.simple_tag
def get_name_tag(instance):
    return instance.tags.get('Name', '')
