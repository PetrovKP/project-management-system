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


class TicketManager(models.Manager):

    @staticmethod
    def get_open_tickets(project_id):
        return Ticket.objects.filter(project_id=project_id, status=TicketStatus.objects.get(title="Open"))

    @staticmethod
    def get_in_progress_tickets(project_id):
        return Ticket.objects.filter(project_id=project_id, status=TicketStatus.objects.get(title="In progress"))

    @staticmethod
    def get_done_tickets(project_id):
        return Ticket.objects.filter(project_id=project_id, status=TicketStatus.objects.get(title="Done"))


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
    reporter = models.ForeignKey(User, related_name='reporter')
    status = models.ForeignKey(TicketStatus, on_delete=models.PROTECT)
    created_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    time_estimated = models.IntegerField() #probably change to float
    time_remaining = models.IntegerField() #do not forget to decrement after logged time added
    time_logged = models.IntegerField()

    def __str__(self):
        return self.title

