from django.conf.urls import url, include
from .views import *

urlpatterns = [

    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^$', AllProjectsView.as_view(), name='index'),
    url(r'^project/(?P<project_id>[0-9]+)$', ProjectView.as_view(), name='project'),
    url(r'^project/(?P<project_id>[0-9]+)/ticket/(?P<ticket_id>[0-9]+)', TicketView.as_view(), name='ticket'),
    url(r'^project/(?P<project_id>[0-9]+)/ticket/new', CreationTicketView.as_view(), name='new_ticket'),
]

