from django.contrib.auth.models import Group

new_groups = ['Spotify Users', 'Pastebin Users', 'Custom Page Users', 'Help Desk Admins', 'Integration Admins', 'All Admins']

for group in new_groups:
    new_group, created = Group.objects.get_or_create(name=group)
