from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Transaction

User = get_user_model()



class TransactionTest(TestCase):
    fixtures = ["datas.json",]

    def setUp(self):
        self.client = Client()
        self.url = reverse("home")
        self.ajax_url = reverse("ajax")

    def login(self, username):
        return self.client.post(
            f'{reverse("admin:login")}?next={self.url}',
            {"username": username, "password": "a"},
            follow=True,
        )

    def test_login_and_make_transaction(self):
        response = self.client.get(self.url, follow=True)
        self.assertInHTML("<title>Log in | Django site admin</title>", response.content.decode())

        # login as suhail and pay 10$ to nusra
        response = self.login('7356775981')

        self.assertContains(response, "Welcome back, Suhail")
        self.assertContains(response, "$0")

        response = self.client.post(
            self.url,
            {"receiver": "8921513696", "amount": 10, "description": "caring"},
            follow=True,
        )
        
        # check suhail has -10$ balance
        self.assertEqual(response.resolver_match.url_name, "pay_success")
        self.assertContains(response, "Payment Successful")
        self.assertContains(response, "Transaction #1")
        self.assertContains(response, "Welcome back, Suhail")
        self.assertContains(response, "$-10")
        response = self.client.get(reverse("transactions"))
        self.assertContains(response, "Paid to Nusra")

        # prevent transaction to own account
        response = self.client.post(
            self.url,
            {"receiver": "7356775981", "amount": 10, "description": "caring"},
            follow=True,
        )
        self.assertContains(response, "Welcome back, Suhail")
        self.assertContains(response, "$-10")

        
        # login as nusra. check she has 10$ balance
        response = self.login("8921513696")
        self.assertContains(response, "Welcome back, Nusra")
        self.assertContains(response, "$10")
        response = self.client.get(reverse("transactions"))
        self.assertContains(response, "Received from Suhail")

    def test_unknown_receiver_is_rejected_without_creating_transaction(self):
        self.login('7356775981')

        response = self.client.post(
            self.url,
            {"receiver": "9000000000", "amount": 10, "description": "caring"},
            follow=True,
        )
        self.assertContains(response, "Receiver account does not exist.")
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertEqual(User.objects.get(username='7356775981').balance, 0)

    def test_negative_amount_is_rejected(self):
        self.login('7356775981')

        response = self.client.post(
            self.url,
            {"receiver": "8921513696", "amount": -10, "description": "refund-ish"},
            follow=True,
        )
        self.assertContains(response, "Ensure this value is greater than or equal to 1.")
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertEqual(User.objects.get(username='7356775981').balance, 0)
        self.assertEqual(User.objects.get(username='8921513696').balance, 0)

    def test_ajax_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(User.objects.get(username='7356775981'))

        response = csrf_client.post(self.ajax_url, {"username": "8921513696"})

        self.assertEqual(response.status_code, 403)

    def test_ajax_returns_json_for_valid_receiver(self):
        self.login('7356775981')

        response = self.client.post(self.ajax_url, {"username": "8921513696"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"first_name": "Nusra"})

    def test_logout_redirects_to_login(self):
        self.login('7356775981')

        response = self.client.post(reverse("logout"), follow=True)

        self.assertRedirects(response, "/admin/login/")
        response = self.client.get(self.url, follow=True)
        self.assertInHTML("<title>Log in | Django site admin</title>", response.content.decode())
