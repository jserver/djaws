from django.conf.urls import patterns
from django.contrib import admin
from django.shortcuts import render

from models import (Build, Bundle, Group, GroupItem,
                    Image, Instance, Key, LinuxUser, Project,
                    PythonBundle, Script, SecurityGroup)


class BuildAdmin(admin.ModelAdmin):
    filter_horizontal = ('security_groups',)


class BundleAdmin(admin.ModelAdmin):
    pass


class GroupItemAdmin(admin.ModelAdmin):
    pass


class GroupItemInline(admin.TabularInline):
    model = Group.items.through


class GroupAdmin(admin.ModelAdmin):
    inlines = (GroupItemInline,)


class ImageAdmin(admin.ModelAdmin):
    pass


class InstanceAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super(InstanceAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^my_view/$', self.admin_site.admin_view(self.my_view))
        )
        return my_urls + urls

    def my_view(self, request):
        context = {
            'current_app': self.admin_site.name
        }
        template = 'admin/projects/my_view.html'
        return render(request, template, context)


class KeyAdmin(admin.ModelAdmin):
    pass


class LinuxUserAdmin(admin.ModelAdmin):
    pass


class ProjectAdmin(admin.ModelAdmin):
    pass


class PythonBundleAdmin(admin.ModelAdmin):
    pass


class ScriptAdmin(admin.ModelAdmin):
    pass


class SecurityGroupAdmin(admin.ModelAdmin):
    pass


admin.site.register(Build, BuildAdmin)
admin.site.register(Bundle, BundleAdmin)
admin.site.register(GroupItem, GroupItemAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Instance, InstanceAdmin)
admin.site.register(Key, KeyAdmin)
admin.site.register(LinuxUser, LinuxUserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(PythonBundle, PythonBundleAdmin)
admin.site.register(Script, ScriptAdmin)
admin.site.register(SecurityGroup, SecurityGroupAdmin)
