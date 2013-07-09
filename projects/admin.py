from django.conf.urls import patterns
from django.contrib import admin
from django.shortcuts import redirect, render

import boto

from models import (Address, Build, Bundle, Group, Image,
                    Instance, Key, LinuxUser, Project,
                    PythonBundle, Script, SecurityGroup)


class AddressAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        conn = boto.connect_ec2()
        addresses = conn.get_all_addresses()

        context = {
            'current_app': self.admin_site.name,
            'addresses': addresses,
        }
        template = 'admin/projects/address/list.html'
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
        template = 'admin/projects/address/associate.html'
        return render(request, template, context)

    def disassociate_view(self, request):
        context = {
            'current_app': self.admin_site.name,
        }
        template = 'admin/projects/address/disassociate.html'
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
            'instances': instances,
        }
        template = 'admin/projects/instance/list.html'
        return render(request, template, context)

    def get_urls(self):
        urls = super(InstanceAdmin, self).get_urls()
        custom_urls = patterns('',
            (r'^reboot/$', self.admin_site.admin_view(self.reboot_view)),
            (r'^start/$', self.admin_site.admin_view(self.start_view)),
            (r'^stop/$', self.admin_site.admin_view(self.stop_view)),
            (r'^terminate/$', self.admin_site.admin_view(self.terminate_view)),
        )
        return custom_urls + urls

    def reboot_view(self, request):
        context = {
            'current_app': self.admin_site.name,
        }
        template = 'admin/projects/instance/reboot.html'
        return render(request, template, context)

    def start_view(self, request):
        context = {
            'current_app': self.admin_site.name,
        }
        template = 'admin/projects/instance/reboot.html'
        return render(request, template, context)

    def stop_view(self, request):
        context = {
            'current_app': self.admin_site.name,
        }
        template = 'admin/projects/instance/reboot.html'
        return render(request, template, context)

    def terminate_view(self, request):
        context = {
            'current_app': self.admin_site.name,
        }
        template = 'admin/projects/instance/reboot.html'
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

        return redirect('/admin/projects/key/')


class LinuxUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name')


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'build', 'count', 'linux_user', 'user_script')


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

        return redirect('/admin/projects/securitygroup/')


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
