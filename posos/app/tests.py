from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from .forms import TicketForm, TicketAssigneeFormManager, ProjectDevelopersForm, TicketStatusForm, ProjectStatusForm
from .models import Project, TicketStatus, ProjectStatus


#  Тестирование логики работы менеджера
class ManagerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_manager = User.objects.create_user(username="manager1", password="password1")
        cls.user_manager.save()
        cls.user_executor1 = User.objects.create_user(username="executor1", password="password1")
        cls.user_executor1.save()

        cls.project = Project.objects.create(id=1,
                                             title='project',
                                             description='efwfefwe',
                                             status_id=0,
                                             due_date="2017-12-23")
        cls.project.save()

        cls.project.manager.add(cls.user_manager)
        cls.project.developers.add(cls.user_executor1)

    def setUp(self):
        self.factory = RequestFactory()

    def test_can_login(self):
        """Проверка на возможность авторизироваться в систему"""
        isLogin = self.client.login(username="manager1", password="password1")

        response = self.client.get('/', follow=True)

        self.assertTrue(isLogin)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/all_projects_template.html")

    def test_cant_login(self):
        """Проверка на отказ авторизироваться в систему, в случае неверного пароля"""
        isLogin = self.client.login(username="manager1", password="passwerrsdfa")

        response = self.client.get('/', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(isLogin)

    def test_can_create_ticket(self):
        """Проверка на возможность создать тикет"""
        user = User.objects.filter(username="executor1")

        form_ticket_data = {'title':'addtests', 'assignee': user, 'description': 'impl',
                            'due_date' : '2017-12-20', 'time_estimated': 2}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)

        self.assertTrue(form_ticket.is_valid())

        response = self.client.post('/project/1', form_ticket.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)
        #self.assertTemplateUsed(response, "app/creation_ticket_template.html")

    def test_cant_create_ticket_format_data(self):
        """Проверка на отсутствие возможности создать тикет из-за неправильной даты"""
        user = User.objects.filter(username="executor1")
        form_ticket_data = {'title':'addtests', 'assignee': user, 'description': 'impl',
                            'due_date' : 'dwed/d', 'time_estimated': 2}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)
        self.assertFalse(form_ticket.is_valid())

    def test_cant_create_ticket_format_time_estimated(self):
        """Проверка на отсутствие возможности создать тикет из-за неправильного ввода оценочного времени"""
        user = User.objects.filter(username="executor1")
        form_ticket_data = {'title': 'addtests', 'assignee': user, 'description': 'impl',
                            'due_date': '2017-12-20', 'time_estimated': 'efwef'}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)
        self.assertFalse(form_ticket.is_valid())

    def test_cant_create_ticket_format_long_title(self):
        """Проверка на отсутствие возможности создать тикет из-за нарушения ограничения по размеру загаловка"""
        user = User.objects.filter(username="executor1")
        form_ticket_data = {'title': 'addtests'*100, 'description': 'impl',
                            'due_date': '2017-12-20', 'assignee': user, 'time_estimated': '3'}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)
        self.assertFalse(form_ticket.is_valid())

    def test_cant_create_ticket_empty_title(self):
        """Проверка на отсутствие возможности создать тикет из-за отсутствия загаловка"""
        user = User.objects.filter(username="executor1")
        form_ticket_data = {'description': 'impl',
                            'due_date': '2017-12-20', 'assignee': user, 'time_estimated': '3'}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)
        self.assertFalse(form_ticket.is_valid())

    def test_cant_create_ticket_empty_user(self):
        """Проверка на отсутствие возможности создать тикет из-за отсутствия исполнителя"""
        form_ticket_data = {'title': 'addtests', 'description': 'impl',
                            'due_date': '2017-12-20', 'time_estimated': '3'}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)
        self.assertFalse(form_ticket.is_valid())

    def test_can_change_executor(self):
        """Проверка на возможность смены исполнителя в задаче"""
        user = User.objects.filter(username="executor1")
        form_ticket_data = {'title':'addtests', 'assignee': user, 'description': 'impl',
                            'due_date' : '2017-12-20', 'time_estimated': 2}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)

        self.assertTrue(form_ticket.is_valid())
        response = self.client.post('/project/1', form_ticket.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/project/1/ticket/1', follow=True)
        self.assertEqual(response.status_code, 200)
        #self.assertTemplateUsed(response, "app/ticket_template.html")
        form_assignee_data = {'assignee': self.project.get_developers()}
        form_assignee = TicketAssigneeFormManager(project_id=1, data=form_assignee_data)

        self.assertTrue(form_assignee.is_valid())

        response = self.client.post('/project/1/ticket/1', form_assignee.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)
        #self.assertTemplateUsed(response, "app/creation_ticket_template.html")

    def test_cant_change_executor_not_projects(self):
        """Проверка на отсутствие возможности смены исполнителя в задаче из-за отсутвия пользователя в проекте"""
        user = User.objects.filter(username="executor1")
        form_ticket_data = {'title':'addtests', 'assignee': user, 'description': 'impl',
                            'due_date' : '2017-12-20', 'time_estimated': 2}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)

        self.assertTrue(form_ticket.is_valid())
        response = self.client.post('/project/1', form_ticket.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/project/1/ticket/1', follow=True)
        self.assertEqual(response.status_code, 200)
        #self.assertTemplateUsed(response, "app/ticket_template.html")
        user_executor_new = User.objects.create_user(username="executor3", password="password1")
        user_executor_new.save()
        user = User.objects.filter(username="executor3")

        form_assignee_data = {'assignee': user}
        form_assignee = TicketAssigneeFormManager(project_id=1, data=form_assignee_data)

        self.assertFalse(form_assignee.is_valid())

    def test_can_add_executor_in_project(self):
        """Проверка на возможность добавления исполнителя в проект"""

        response = self.client.get('/project/1', follow=True)
        self.assertEqual(response.status_code, 200)
        #self.assertTemplateUsed(response, "app/ticket_template.html")

        user_executor_new = User.objects.create_user(username="executor3", password="password1")
        user_executor_new.save()
        user = User.objects.filter(username="executor3")
        form_develops_data = {'developers': user}
        form_develops = ProjectDevelopersForm(data=form_develops_data)

        self.assertTrue(form_develops.is_valid())

        response = self.client.post('/project/1', form_develops.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_can_add_executor_in_project_myself_project(self):
        """Проверка на отсутствие ошибок при добавлении исполнителя в проект, когда он уже есть"""
        response = self.client.get('/project/1', follow=True)
        self.assertEqual(response.status_code, 200)
        user = User.objects.filter(username="executor1")
        form_develops_data = {'developers': user}
        form_develops = ProjectDevelopersForm(data=form_develops_data)

        self.assertTrue(form_develops.is_valid())

        response = self.client.post('/project/1', form_develops.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_can_remove_executor_in_project(self):
        """Проверка на возможность удаление исполнителя из проекта"""
        response = self.client.get('/project/1', follow=True)
        self.assertEqual(response.status_code, 200)
        user_executor_new = User.objects.create_user(username="executor3", password="password1")
        user_executor_new.save()
        user = User.objects.filter(username="executor3")
        form_develops_data = {'developers': user}
        form_develops = ProjectDevelopersForm(data=form_develops_data)

        self.assertTrue(form_develops.is_valid())

        response = self.client.post('/project/1', form_develops.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)

        user = User.objects.filter(username="executor")
        form_develops_data = {'developers': user}
        form_develops = ProjectDevelopersForm(data=form_develops_data)

        self.assertTrue(form_develops.is_valid())

        response = self.client.post('/project/1', form_develops.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_can_change_task_status(self):
        """Проверка на возможность изменения статуса проекта"""
        response = self.client.get('/project/1', follow=True)
        self.assertEqual(response.status_code, 200)

        status = ProjectStatus.objects.create(title="DO")
        status.save()
        status = ProjectStatus.objects.filter(title="DO")

        form_status_data = {'status': status}
        form_status = ProjectStatusForm(data=form_status_data)

        self.assertTrue(form_status.is_valid())

        response = self.client.post('/project/1', form_status.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)


    def test_can_change_projects_status(self):
        """Проверка на возможность изменения статуса задачи"""
        user = User.objects.filter(username="executor1")
        form_ticket_data = {'title':'addtests', 'assignee': user, 'description': 'impl',
                            'due_date' : '2017-12-20', 'time_estimated': 2}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)

        self.assertTrue(form_ticket.is_valid())
        response = self.client.post('/project/1', form_ticket.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/project/1/ticket/1', follow=True)
        self.assertEqual(response.status_code, 200)

        status = TicketStatus.objects.create(title="DO")
        status.save()
        status = TicketStatus.objects.filter(title="DO")

        form_status_data = {'status': status}
        form_status = TicketStatusForm(data=form_status_data)

        self.assertTrue(form_status.is_valid())

        response = self.client.post('/project/1', form_status.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)


#  Тестирование логики работы исполнителя
class ExecutorTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_manager = User.objects.create_user(username="manager1", password="password1")
        cls.user_manager.save()
        cls.user_executor = User.objects.create_user(username="executor", password="password1")
        cls.user_executor.save()
        cls.project = Project.objects.create(id=1,
                                             title='project',
                                             description='efwfefwe',
                                             status_id=0,
                                             due_date="2017-12-23")
        cls.project.save()

        cls.project.manager.add(cls.user_manager)
        cls.project.developers.add(cls.user_executor)


    def test_can_login(self):
        """Проверка на возможность авторизироваться в систему"""
        isLogin = self.client.login(username="executor", password="password1")

        response = self.client.get('/', follow=True)

        self.assertTrue(isLogin)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/all_projects_template.html")

    def test_cant_login(self):
        """Проверка на отказ авторизироваться в систему, в случае неверного пароля"""
        isLogin = self.client.login(username="executor1", password="passwerrsdfa")

        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(isLogin)

    def test_can_appoint_myself(self):
        """Проверка на возможность назначения задачи на себя"""
        user = User.objects.filter(username="executor")
        form_ticket_data = {'title':'addtests', 'assignee':user, 'description': 'impl',
                            'due_date' : '2017-12-20', 'time_estimated': 2}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)

        self.assertTrue(form_ticket.is_valid())
        self.client.post('/project/1', form_ticket.cleaned_data, follow=True)

        form_assignee_data = {'assignee': user}
        form_assignee = TicketAssigneeFormManager(project_id=1, data=form_assignee_data)

        self.assertTrue(form_assignee.is_valid())

        response = self.client.post('/project/1/ticket/1', form_assignee.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_cant_appoint_myself(self):
        """Проверка на отсутствие возможности назначения задачи на других"""
        user = User.objects.filter(username="executor_ref")
        form_ticket_data = {'title':'addtests', 'assignee':user, 'description': 'impl',
                            'due_date' : '2017-12-20', 'time_estimated': 2}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)

        self.assertFalse(form_ticket.is_valid())

    def test_can_change_task_status(self):
        """Проверка на возможность сменить статус задачи"""
        user = User.objects.filter(username="executor")
        form_ticket_data = {'title':'addtests', 'assignee': user, 'description': 'impl',
                            'due_date' : '2017-12-20', 'time_estimated': 2}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)

        self.assertTrue(form_ticket.is_valid())
        response = self.client.post('/project/1', form_ticket.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/project/1/ticket/1', follow=True)
        self.assertEqual(response.status_code, 200)

        status = TicketStatus.objects.create(title="DO")
        status.save()
        status = TicketStatus.objects.filter(title="DO")

        form_status_data = {'status': status}
        form_status = TicketStatusForm(data=form_status_data)

        self.assertTrue(form_status.is_valid())

        response = self.client.post('/project/1', form_status.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_can_set_task_execution_time(self):
        """Проверка на возможность установить время выполнения задачи"""
        user = User.objects.filter(username="executor")
        form_ticket_data = {'title':'addtests', 'assignee': user, 'description': 'impl',
                            'due_date' : '2017-12-20', 'time_estimated': 2}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)
        self.assertTrue(form_ticket.is_valid())
        response = self.client.post('/project/1', form_ticket.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/project/1/ticket/1', follow=True)
        self.assertEqual(response.status_code, 200)

        form_logger_data = {'time_logged': 10}
        form_logger = TicketStatusForm(data=form_logger_data)

        self.assertTrue(form_logger.is_valid())

        response = self.client.post('/project/1/ticket/1', form_logger.cleaned_data, follow=True)
        self.assertEqual(response.status_code, 200)
