from django.forms import ModelForm, DateInput, ModelChoiceField

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


class ProjectDevelopersForm(ModelForm):
    class Meta:
        model = Project
        fields = ['developers']


class TicketStatusForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['status']


class TicketAssigneeForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['assignee']

    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('project_id')
        super(TicketAssigneeForm, self).__init__(*args, **kwargs)
        developers = Project.objects.get(id=project_id).developers
        developers_forms = ModelChoiceField(queryset=developers)
        self.fields['assignee'] = developers_forms


class TicketTimeRemainingForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['time_remaining']


class TicketTimeLoggedForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['time_logged']
