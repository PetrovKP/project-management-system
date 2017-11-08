from django.conf.urls import url, include
from .views import *


from django.contrib.auth import views as auth_views


urlpatterns = [

    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^$', AllProjectsView.as_view(), name='index'),
    url(r'^project/(?P<project_id>[0-9]+$)', ProjectView.as_view(), name='project'),
]

