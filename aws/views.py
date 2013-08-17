from django.shortcuts import render

import boto

from aws.models import Build, Project
from aws.tasks import build_task, project_task


# Create your views here.
def index(request):
    conn = boto.connect_ec2()
    reservations = conn.get_all_instances()
    instances = []
    for res in reservations:
        for instance in res.instances:
            instances.append(instance)

    addresses = conn.get_all_addresses()

    context = {
        'addresses': addresses,
        'instances': instances,
    }
    template = 'aws/index.html'
    return render(request, template, context)


def launch(request):
    #conn = boto.connect_ec2()
    builds = Build.objects.all()
    projects = Project.objects.all()

    context = {
        'builds': builds,
        'projects': projects,
    }
    template = 'aws/launch.html'
    return render(request, template, context)


def launch_build(request, build_name):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name')
        build = Build.objects.get(name=build_name)
        result = build_task.delay(build, name)
        context['result'] = result
    template = 'aws/build.html'
    return render(request, template, context)


def launch_project(request, project_name):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name')
        project = Project.objects.get(name=project_name)
        result = project_task.delay(project, name)
        context['result'] = result
    template = 'aws/project.html'
    return render(request, template, context)
