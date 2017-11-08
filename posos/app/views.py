from django.views.generic import TemplateView
from .models import Project


class AllProjectsView(TemplateView):
    template_name = "app/all_projects_template.html"

    def get_context_data(self, **kwargs):
        context = super(AllProjectsView, self).get_context_data()
        context['projects'] = Project.objects.all()
        return context
