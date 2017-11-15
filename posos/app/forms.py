from django.forms import ModelForm, DateInput

from .models import Ticket, Project


class DateInputt(DateInput):
    input_type = 'date'


class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'assignee', 'status', 'due_date', 'time_estimated']
        widgets = {
            'due_date': DateInputt(),
        }


class ProjectStatusForm(ModelForm):
    class Meta:
        model = Project
        fields = ['status']


class TicketStatusForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['status']

class TicketAssigneeForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['assignee']