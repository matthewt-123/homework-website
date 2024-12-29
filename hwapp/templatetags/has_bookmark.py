from django import template

register = template.Library()

@register.filter(name='has_bookmark')
def has_bookmark(user, template_id):
    return user.bookmarks.filter(id=template_id).exists()