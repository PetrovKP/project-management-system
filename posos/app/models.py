from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class ProjectManager(models.Manager):

    @staticmethod
    def get_all_for_user(user):
        return Project.objects.filter(Q(developers=user) | Q(manager=user)).distinct()

    @staticmethod
    def is_user_associated(user, project_id):
        project = Project.objects.get(id=project_id)
        return user in project.manager.all() or user in project.developers.all()

    @staticmethod
    def is_user_project_manager(user, project_id):
        project = Project.objects.get(id=project_id)
        return user in project.manager.all()


class TicketManager(models.Manager):

    @staticmethod
    def save_ticket(title, description, project, assignee, reporter, status, due_date, time_estimated):
        return Ticket(title=title, description=description, project=project, assignee=assignee, reporter=reporter,
                      status=status, due_date=due_date, time_estimated=time_estimated).save()

    @staticmethod
    def save_ticket_form_form(form, project_id, user):
        ticket = form.save(commit=False)
        ticket.project = Project.objects.get(id=project_id)
        ticket.reporter = user
        return ticket.save()


class TicketStatus(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class ProjectStatus(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class Project(models.Model):
    title = models.CharField(max_length=40)
    description = models.TextField()
    manager = models.ManyToManyField(User, related_name='managers')
    developers = models.ManyToManyField(User, related_name='developers')
    status = models.ForeignKey(ProjectStatus, on_delete=models.PROTECT)
    created_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()

    objects = ProjectManager()

    def __str__(self):
        return self.title


class Ticket(models.Model):
    title = models.CharField(max_length=40)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, related_name='assignee')
    reporter = models.ForeignKey(User, related_name='reporter', blank=True, null=True)
    status = models.ForeignKey(TicketStatus, on_delete=models.PROTECT)
    created_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    time_estimated = models.IntegerField()  # probably change to float
    time_remaining = models.IntegerField(blank=True)  # do not forget to decrement after logged time added
    time_logged = models.IntegerField(default=0)

    objects = TicketManager()

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, *args, **kwargs):
        if self.status is None:
            self.status = TicketStatus.objects.get(title="Open")
        if self.time_remaining is None:
            self.time_remaining = self.time_estimated
        super(Ticket, self).save(*args, **kwargs)
