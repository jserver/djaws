from django import forms
from django.conf.urls import patterns
from django.contrib import admin
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

import boto

from aws.models import (Address, Build, Bundle, Group, Image,
                        Instance, Key, LinuxUser, Project,
                        PythonBundle, Script, SecurityGroup)
from aws.tasks import build_task
from aws.utils import load_keys, load_security_groups


class AddressAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        conn = boto.connect_ec2()
        addresses = conn.get_all_addresses()

        reservations = conn.get_all_instances()
        instances = []
        for res in reservations:
            for instance in res.instances:
                if (instance.state != "terminated" and
                    instance.id not in [address.instance_id for address in addresses]):
                    instances.append(instance)

        context = {
            'current_app': self.admin_site.name,
            'app_label': 'aws',
            'addresses': addresses,
            'instances': instances,
        }
        template = 'admin/aws/address/list.html'
        return render(request, template, context)

    def get_urls(self):
        urls = super(AddressAdmin, self).get_urls()
        custom_urls = patterns('',
            (r'^associate/$', self.admin_site.admin_view(self.associate_view)),
            (r'^disassociate/$', self.admin_site.admin_view(self.disassociate_view)),
        )
        return custom_urls + urls

    def associate_view(self, request):
        context = {
            'current_app': self.admin_site.name,
        }
        template = 'admin/aws/address/associate.html'
        return render(request, template, context)

    def disassociate_view(self, request):
        context = {
            'current_app': self.admin_site.name,
        }
        template = 'admin/aws/address/disassociate.html'
        return render(request, template, context)


class BuildAdmin(admin.ModelAdmin):
    filter_horizontal = ('security_groups',)
    list_display = ('name', 'size', 'image', 'zone', 'group', 'python_bundle')


class BundleAdmin(admin.ModelAdmin):
    list_display = ('name', 'packages')


class GroupItemInline(admin.TabularInline):
    model = Group.items.through


class GroupAdmin(admin.ModelAdmin):
    inlines = (GroupItemInline,)


class ImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_id')


class InstanceAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        conn = boto.connect_ec2()
        reservations = conn.get_all_instances()
        instances = []
        for res in reservations:
            for instance in res.instances:
                instances.append(instance)

        context = {
            'current_app': self.admin_site.name,
            'app_label': 'aws',
            'instances': instances,
        }
        template = 'admin/aws/instance/list.html'
        return render(request, template, context)

    def get_urls(self):
        urls = super(InstanceAdmin, self).get_urls()
        custom_urls = patterns('',
            (r'^launch/$', self.admin_site.admin_view(self.launch_view)),
            (r'^launching/$', self.admin_site.admin_view(self.launching_view)),
            (r'^build/$', self.admin_site.admin_view(self.build_view)),
            (r'^project/$', self.admin_site.admin_view(self.project_view)),
            (r'^reboot/$', self.admin_site.admin_view(self.reboot_view)),
            (r'^start/$', self.admin_site.admin_view(self.start_view)),
            (r'^stop/$', self.admin_site.admin_view(self.stop_view)),
            (r'^terminate/$', self.admin_site.admin_view(self.terminate_view)),
        )
        return custom_urls + urls

    def launch_view(self, request):
        LaunchForm = modelform_factory(Build,
                                       exclude=('name',),
                                       widgets={'security_groups': forms.CheckboxSelectMultiple()})
        if request.method == 'POST':
            form = LaunchForm(request.POST)
            if form.is_valid():
                # What to do, what to do
                # ...
                result = build_task.delay(form=form)
                return HttpResponseRedirect('/admin/aws/instance/launching/?id=%s' % result) # Redirect after POST
        else:
            form = LaunchForm()

        context = {
            'current_app': self.admin_site.name,
            'app_label': 'aws',
            'form': form,
        }
        template = 'admin/aws/instance/launch.html'
        return render(request, template, context)

    def launching_view(self, request):
        task_id = request.GET.get('id', '')
        context = {
            'current_app': self.admin_site.name,
            'app_label': 'aws',
            'task_id': task_id,
        }
        template = 'admin/aws/instance/launching.html'
        return render(request, template, context)

    def build_view(self, request):
        context = {
            'current_app': self.admin_site.name,
        }
        template = 'admin/aws/instance/build.html'
        return render(request, template, context)

    def project_view(self, request):
        context = {
            'current_app': self.admin_site.name,
        }
        template = 'admin/aws/instance/project.html'
        return render(request, template, context)

    def reboot_view(self, request):
        context = {
            'current_app': self.admin_site.name,
        }
        template = 'admin/aws/instance/reboot.html'
        return render(request, template, context)

    def start_view(self, request):
        context = {
            'current_app': self.admin_site.name,
        }
        template = 'admin/aws/instance/start.html'
        return render(request, template, context)

    def stop_view(self, request):
        context = {
            'current_app': self.admin_site.name,
        }
        template = 'admin/aws/instance/stop.html'
        return render(request, template, context)

    def terminate_view(self, request):
        context = {
            'current_app': self.admin_site.name,
        }
        template = 'admin/aws/instance/terminate.html'
        return render(request, template, context)


class KeyAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super(KeyAdmin, self).get_urls()
        custom_urls = patterns('',
            (r'^reload/$', self.admin_site.admin_view(self.reload_view)),
        )
        return custom_urls + urls

    def reload_view(self, request):
        load_keys()
        return redirect('/admin/aws/key/')


class LinuxUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name')


class BuildInline(admin.TabularInline):
    model = Project.builds.through


class ProjectAdmin(admin.ModelAdmin):
    inlines = (BuildInline,)
    list_display = ('name', 'linux_user', 'user_script')


class PythonBundleAdmin(admin.ModelAdmin):
    list_display = ('name', 'packages')


class ScriptAdmin(admin.ModelAdmin):
    pass


class SecurityGroupAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('name', 'description')

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super(SecurityGroupAdmin, self).get_urls()
        custom_urls = patterns('',
            (r'^reload/$', self.admin_site.admin_view(self.reload_view)),
        )
        return custom_urls + urls

    def reload_view(self, request):
        load_security_groups()
        return redirect('/admin/aws/securitygroup/')


admin.site.register(Address, AddressAdmin)
admin.site.register(Build, BuildAdmin)
admin.site.register(Bundle, BundleAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Instance, InstanceAdmin)
admin.site.register(Key, KeyAdmin)
admin.site.register(LinuxUser, LinuxUserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(PythonBundle, PythonBundleAdmin)
admin.site.register(Script, ScriptAdmin)
admin.site.register(SecurityGroup, SecurityGroupAdmin)
