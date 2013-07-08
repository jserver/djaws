from django.conf.urls import patterns, url


urlpatterns = patterns('projects.views',
    url(r'^$', 'index', name='projects-index'),
    url(r'^launch/$', 'launch', name='projects-launch'),
    url(r'^launch/build/(?P<build_name>[-\w]+)/$', 'launch_build', name='projects-launch-build'),
    url(r'^launch/project/(?P<project_name>[-\w]+)/$', 'launch_project', name='projects-launch-project'),
)
