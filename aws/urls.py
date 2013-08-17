from django.conf.urls import patterns, url


urlpatterns = patterns('aws.views',
    url(r'^$', 'index', name='aws-index'),
    url(r'^launch/$', 'launch', name='aws-launch'),
    url(r'^launch/build/(?P<build_name>[-\w]+)/$', 'launch_build', name='aws-launch-build'),
    url(r'^launch/project/(?P<project_name>[-\w]+)/$', 'launch_project', name='aws-launch-project'),
)
