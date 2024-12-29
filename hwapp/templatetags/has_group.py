from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    if user.groups.filter(name=group_name).exists() or user.is_superuser:
        return True
    else:
        return False