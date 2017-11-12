from django.test import TestCase
from django.contrib.auth.models import User
from .models import Project, Ticket, TicketStatus


class AdminTest(TestCase):
    class MenegerTest(TestCase):
        @classmethod
        def setUpTestData(cls):
            cls.superuser = User.objects.create_superuser(username="admin", password="password")
        def setUp(self):
            self.client.login(username="admin", password="password")
        def tearDown(self):
            self.client.logout()

#  Функционал для менеджера

class MenegerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="manager1", password="password1")

    def setUp(self):
        # self.project = Project.
        pass

    def test_can_login(self):
        """Проверка на возможность авторизироваться в систему"""
        responce = self.client.login(usernane="manager1", password="password1")

        self.assertEqual(responce.status_code, 200)

    def test_cant_login(self):
        """Проверка на отказ авторизироваться в систему, в случае неверного пароля"""
        responce = self.client.login("manager1", "pass")

        self.assertNotEqual(responce.status_code, 200)

    def test_can_create_ticket(self):
        """Проверка на возможность создать тикет"""
        responce = self.client.post('/', {'title':'add tests', 'description': 'impl'})

        self.assertEqual(responce.status_code, 200)

