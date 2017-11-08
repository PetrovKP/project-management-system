from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import Project, Ticket, TicketStatus


class AccessToProjectMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        if Project.objects.is_user_associated(request.user, project_id):
            return super(AccessToProjectMixin, self).dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()


class AllProjectsView(LoginRequiredMixin, TemplateView):
    template_name = "app/all_projects_template.html"

    def get_context_data(self, **kwargs):
        context = super(AllProjectsView, self).get_context_data()
        context['projects'] = Project.objects.get_all_for_user(self.request.user)
        return context


class ProjectView(AccessToProjectMixin, TemplateView):
    template_name = "app/project_template.html"

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data()
        project_id = kwargs['project_id']
        context['project'] = Project.objects.get(id=project_id)
        context['tickets'] = Ticket.objects.filter(project__id=project_id)
        context['status_list'] = TicketStatus.objects.all()
        return context


class TicketView(AccessToProjectMixin, TemplateView):
    template_name = "app/ticket_template.html"

    def get_context_data(self, **kwargs):
        context = super(TicketView, self).get_context_data()
        ticket_id = kwargs['ticket_id']
        context['ticket'] = Ticket.objects.get(id=ticket_id)
        return context
