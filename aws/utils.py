import boto

from aws.models import Key, SecurityGroup


def load_keys():
    conn = boto.connect_ec2()
    all_key_pairs = conn.get_all_key_pairs()
    aws_keys = set(key.name for key in all_key_pairs)

    keys = Key.objects.all()
    dj_keys = set(key.name for key in keys)

    deleted_keys = dj_keys.difference(aws_keys)
    if deleted_keys:
        Key.objects.filter(name__in=deleted_keys).delete()

    new_keys = aws_keys.difference(dj_keys)
    for new_key in new_keys:
        aws_key = [key for key in all_key_pairs if key.name == new_key][0]
        Key.objects.create(name=aws_key.name)


def load_security_groups():
        conn = boto.connect_ec2()
        all_security_groups = conn.get_all_security_groups()
        aws_groups = set(grp.id for grp in all_security_groups)

        security_groups = SecurityGroup.objects.all()
        dj_groups = set(grp.id for grp in security_groups)

        deleted_groups = dj_groups.difference(aws_groups)
        if deleted_groups:
            SecurityGroup.objects.filter(id__in=deleted_groups).delete()

        new_groups = aws_groups.difference(dj_groups)
        for new_group_id in new_groups:
            aws_group = [group for group in all_security_groups if group.id == new_group_id][0]
            SecurityGroup.objects.create(id=aws_group.id, name=aws_group.name, description=aws_group.description)
