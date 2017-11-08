from django.contrib import admin
from .models import *

admin.site.register(TicketStatus);
admin.site.register(ProjectStatus);
admin.site.register(Project);
admin.site.register(Ticket);

# Register your models here.
