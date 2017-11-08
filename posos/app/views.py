from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import Project


class AllProjectsView(LoginRequiredMixin, TemplateView):
    template_name = "app/all_projects_template.html"

    def get_context_data(self, **kwargs):
        context = super(AllProjectsView, self).get_context_data()
        context['projects'] = Project.objects.get_all_for_user(self.request.user)
        return context
