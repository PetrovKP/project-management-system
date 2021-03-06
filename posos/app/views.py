from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, FormView

from .view.generic.multiform import MultiFormsView
from .models import Project, Ticket, TicketStatus
from .forms import *


class AccessToProjectMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        if Project.objects.is_user_associated(request.user, project_id):
            return super(AccessToProjectMixin, self).dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()


class ProjectManagerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        if Project.objects.is_user_project_manager(request.user, project_id):
            return super(ProjectManagerRequiredMixin, self).dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()


class AllProjectsView(LoginRequiredMixin, TemplateView):
    template_name = "app/all_projects_template.html"

    def get_context_data(self, **kwargs):
        context = super(AllProjectsView, self).get_context_data()
        context['projects'] = Project.objects.get_all_for_user(self.request.user)
        return context


class ProjectView(AccessToProjectMixin, MultiFormsView):
    template_name = "app/project_template.html"
    form_classes = {'ticket': TicketForm,
                    'status': ProjectStatusForm,
                    'developers': ProjectDevelopersForm}
    success_url = '/'

    def get_form_kwargs(self, form_name, bind_form=False):
        kw = super(ProjectView, self).get_form_kwargs(form_name, bind_form=bind_form)
        if form_name == 'ticket':
            kw['project_id'] = self.kwargs['project_id']
        return kw

    def get_status_initial(self):
        return {'status': Project.objects.get(id=self.kwargs['project_id']).get_status()}

    def get_developers_initial(self):
        return {'developers': Project.objects.get(id=self.kwargs['project_id']).get_developers()}

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        project_id = self.kwargs['project_id']
        context['project'] = Project.objects.get(id=project_id)
        context['tickets'] = Ticket.objects.filter(project__id=project_id)
        context['status_list'] = TicketStatus.objects.all()
        return context

    def ticket_form_valid(self, form):
        project_id = self.kwargs['project_id']
        self.success_url = reverse('project', args=project_id)
        Ticket.objects.save_ticket_form_form(form, project_id, self.request.user)
        return HttpResponseRedirect(self.get_success_url())

    def status_form_valid(self, form):
        project_id = self.kwargs['project_id']
        self.success_url = reverse('project', args=project_id)
        status = form.cleaned_data['status']
        Project.objects.update_project_status(status, project_id)
        return HttpResponseRedirect(self.get_success_url())

    def developers_form_valid(self, form):
        project_id = self.kwargs['project_id']
        self.success_url = reverse('project', args=project_id)
        developers = form.cleaned_data['developers']
        Project.objects.update_developers_list(developers, project_id)
        return HttpResponseRedirect(self.get_success_url())


class TicketView(AccessToProjectMixin, MultiFormsView):
    template_name = "app/ticket_template.html"
    form_classes = {'status': TicketStatusForm,
                    'assignee_manager': TicketAssigneeFormManager,
                    'assignee_user': TicketAssigneeFormDeveloper,
                    'time_remaining': TicketTimeRemainingForm,
                    'time_logged': TicketTimeLoggedForm}
    success_url = '/'

    def get_form_kwargs(self, form_name, bind_form=False):
        kw = super(TicketView, self).get_form_kwargs(form_name, bind_form=bind_form)
        if form_name == 'assignee_manager':
            kw['project_id'] = self.kwargs['project_id']
        elif form_name == 'assignee_user':
            kw.update({
                'user': self.request.user,
                'project_id': self.kwargs['project_id']})
        return kw

    def get_context_data(self, **kwargs):
        context = super(TicketView, self).get_context_data(**kwargs)
        ticket_id = self.kwargs['ticket_id']
        project_id = self.kwargs['project_id']
        context['ticket'] = Ticket.objects.get(id=ticket_id)
        context['project'] = Project.objects.get(id=project_id)
        return context

    def status_form_valid(self, form):
        self.success_url = reverse('ticket', args=(self.kwargs['project_id'], self.kwargs['ticket_id'],))
        status = form.cleaned_data['status']
        Ticket.objects.update_ticket_status(status, self.kwargs['ticket_id'])
        return HttpResponseRedirect(self.get_success_url())

    def get_status_initial(self):
        return {'status': Ticket.objects.get(id=self.kwargs['ticket_id']).get_status()}

    def assignee_manager_form_valid(self, form):
        self.success_url = reverse('ticket', args=(self.kwargs['project_id'], self.kwargs['ticket_id'],))
        assignee = form.cleaned_data['assignee']
        Ticket.objects.update_ticket_assignee(assignee, self.kwargs['ticket_id'])
        return HttpResponseRedirect(self.get_success_url())

    def get_assignee_manager_initial(self):
        return {'assignee': Ticket.objects.get(id=self.kwargs['ticket_id']).get_assignee()}

    def assignee_user_form_valid(self, form):
        self.success_url = reverse('ticket', args=(self.kwargs['project_id'], self.kwargs['ticket_id'],))
        assignee = form.cleaned_data['assignee']
        Ticket.objects.update_ticket_assignee(assignee, self.kwargs['ticket_id'])
        return HttpResponseRedirect(self.get_success_url())

    def time_remaining_form_valid(self, form):
        self.success_url = reverse('ticket', args=(self.kwargs['project_id'], self.kwargs['ticket_id'],))
        time_remaining = form.cleaned_data['time_remaining']
        Ticket.objects.update_ticket_remaining_time(time_remaining, self.kwargs['ticket_id'])
        return HttpResponseRedirect(self.get_success_url())

    def get_time_remaining_initial(self):
        return {'time_remaining': Ticket.objects.get(id=self.kwargs['ticket_id']).get_time_remaining()}

    def time_logged_form_valid(self, form):
        self.success_url = reverse('ticket', args=(self.kwargs['project_id'], self.kwargs['ticket_id'],))
        time_logged = form.cleaned_data['time_logged']
        Ticket.objects.update_ticket_logged_time(time_logged, self.kwargs['ticket_id'])
        return HttpResponseRedirect(self.get_success_url())

    def get_time_logged_initial(self):
        return {'time_logged': 0}


class CreationTicketView(ProjectManagerRequiredMixin, FormView):
    template_name = "app/creation_ticket_template.html"
    form_class = TicketForm
    success_url = '/'

    def form_valid(self, form):
        self.success_url = reverse('project', args=(self.kwargs['project_id'],))
        Ticket.objects.save_ticket_form_form(form, self.kwargs['project_id'], self.request.user)
        return super(CreationTicketView, self).form_valid(form)
