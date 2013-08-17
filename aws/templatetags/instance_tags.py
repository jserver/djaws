from django import template

import boto

register = template.Library()

@register.simple_tag
def get_name_tag(obj):
    instance = None
    if isinstance(obj, str):
        if obj:
            conn = boto.connect_ec2()
            reservations = conn.get_all_instances(instance_ids=[obj])
            for res in reservations:
                for inst in res.instances:
                    if inst.id == obj:
                        instance = inst
                        break
    else:
        instance = obj

    if instance:
        name = instance.tags.get('Name', '')
    else:
        name = ''
    return name
