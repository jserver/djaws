from celery import task
import boto

from aws.models import Build
from aws.utils import get_choice


@task()
def tag_reservation_task(reservation, name):
    count = 0
    for instance in reservation.instances:
        instance.add_tag('Name', name)
        count += 1
    return count


@task()
def build_task(build=None, form=None, name=None, count=1):
    conn = boto.connect_ec2()
    image = conn.get_image(image_id=build.image.image_id)

    if build:
        if not name:
            name = 'from-build'
        kwargs = {
            'key_name': build.key.name,
            'instance_type': build.get_size_display(),
            'security_group_ids': [sg.name for sg in build.security_groups.all()],
        }
        if build.user_data:
            kwargs['user_data'] = build.user_data.data
        if build.zone:
            kwargs['placement'] = build.get_zone_display()
    elif form:
        bld = form.cleaned_data
        if not name:
            name = 'from-form'
        kwargs = {
            'key_name': bld['key'].name,
            'instance_type': get_choice(Build.SIZE_CHOICES,  bld['size']),
            'security_group_ids': [sg.name for sg in bld['security_groups'].all()],
        }
        if bld['user_data']:
            kwargs['user_data'] = bld['user_data'].data
        if bld['zone']:
            kwargs['placement'] = get_choice(Build.ZONE_CHOICES, bld['zone'])
    else:
        pass

    if count > 1:
        kwargs['min_count'] = count
        kwargs['max_count'] = count

    reservation = image.run(**kwargs)
    tag_reservation_task.apply_async((reservation, name), countdown=20)
    return reservation


@task()
def project_task(project, name):
    result = build_task.delay(project.build, name, project.count)
    reservation = result.get()
    return reservation
