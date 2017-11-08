from django.forms import ModelForm, DateInput

from .models import Ticket


class DateInputt(DateInput):
    input_type = 'date'


class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'reporter', 'status', 'due_date', 'time_estimated']
        widgets = {
            'due_date': DateInputt(),
        }