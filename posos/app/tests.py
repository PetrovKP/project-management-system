from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from .forms import TicketForm, TicketAssigneeFormManager, ProjectDevelopersForm, TicketStatusForm
from .models import Project, Ticket, TicketStatus


#  Тестирования администратора
class AdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(username="admin", password="password", email='vasya@mail.ru')
    def setUp(self):
        self.client.login(username="admin", password="password")
    def tearDown(self):
        self.client.logout()

    def test_can_create_project(self):
        """Проверка на возможность создать проект"""
        response = self.client.post('/admin/app/project/add/', {'title' : 'hsrth',
                                                                'description': 'jtyj',
                                                                'manager':'thr',
                                                                'status':'hrt',
                                                                'created_date':'12.11.2017',
                                                                'due_date':'15.11.2017'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/admin/app/project/')
        print(response)
        self.assertEqual(response.status_code, 200)


#  Тестирования менеджера
class MenegerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_manager = User.objects.create_user(username="manager1", password="password1")
        cls.user_manager.save()
        cls.user_executor1 = User.objects.create_user(username="executor1", password="password1")
        cls.user_executor1.save()

        cls.user_executor2 = User.objects.create_user(username="executor2", password="password2")
        cls.project = Project.objects.create(id=1, title='project', description='efwfefwe', status_id=0, due_date="2017-12-23")
        cls.project.save()

        cls.project.manager.add(cls.user_manager)
        cls.project.developers.add(cls.user_executor1)
        cls.project.developers.add(cls.user_executor2)


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
        """Проверка на отсутствие возможности создать тикет из-за неправильного ввода даты"""
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
        """Проверка на отсутствие возможности смены испонителя в задаче из-за отсутвия пользователя в проекте"""
        user = User.objects.filter(username="executor1")
        form_ticket_data = {'title':'addtests', 'assignee': user, 'description': 'impl',
                            'due_date' : '2017-12-20', 'time_estimated': 2}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)
        print(form_ticket.is_valid())
        print(form_ticket.cleaned_data)

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

    def test_can_added_executor_in_project(self):
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

    def test_can_added_executor_in_project_myself_project(self):
        """Проверка на отсутсвие ошибок при добавления исполнителя в проект, когда он уже есть"""

        response = self.client.get('/project/1', follow=True)
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, "app/ticket_template.html")
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
        # self.assertTemplateUsed(response, "app/ticket_template.html")
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

    def test_can_change_task_status2(self):
        """Проверка на возможность изменения статуса задачи"""
        user = User.objects.filter(username="executor1")
        form_ticket_data = {'title': 'addtests', 'assignee': user, 'description': 'impl',
                            'due_date': '2017-12-20', 'time_estimated': 2}
        form_ticket = TicketForm(project_id=1, data=form_ticket_data)

        self.assertTrue(form_ticket.is_valid())
        request = self.factory.get('/project/1')
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


#  Тестирование исполнителей
class ExecutorTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="executor1", password="password1")
        #cls.project = Project.objects.create()
       # cls.ticket = Ticket.objects.save_ticket('sdaa', 'dwdwdwda, )

    def setUp(self):
        # self.project = Project.
        pass

    def test_can_login(self):
        """Проверка на возможность авторизироваться в систему"""
        isLogin = self.client.login(username="executor1", password="password1")

        response = self.client.get('/', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(isLogin)

    def test_cant_login(self):
        """Проверка на отказ авторизироваться в систему, в случае неверного пароля"""
        isLogin = self.client.login(username="executor1", password="passwerrsdfa")

        response = self.client.get('/', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(isLogin)

    def test_can_create_ticket(self):
        """Проверка на возможность создать тикет"""
        response = self.client.post('/', {'title':'add tests', 'description': 'impl',
                                          'assignee' : 'kirill', 'status' : '',
                                          'due_date' : 'tr', 'time_estimated': 'erge'})

        #self.assertEqual(response.status_code, 200)

