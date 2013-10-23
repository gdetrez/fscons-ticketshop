from django.test import Client
from django.contrib.auth.models import User

from django.test import TestCase
from ..models import TicketType, TicketPurchase

class TicketPurchaseViewTest(TestCase):

    def test_getForm(self):
        """
        Test that we can get the purchase form
        """
        self.assertContains(self.client.get("/"), "name")


class TestConfirmationView(TestCase):

    def setUp(self):
        # It appears that client.session only work
        # for non annonymous users: setup Test User
        User.objects.create_user('user', 'user@site.com', 'password')
        # Login
        self.client.login(username='user', password='password')

        # Create data
        tt = TicketType.objects.create( name = "Standard ticket", price = 100 )
        self.purchase = TicketPurchase.objects.create(
            name = "Bruce Wayne",
            email = "bruce@wayneenterprise.com" )
        self.purchase.ticket_set.create( name = "Batman", ticket_type = tt )
        self.purchase.ticket_set.create( name = "Catwoman", ticket_type = tt )
        self.invoice_id = self.purchase.invoice_id

    def test_itRedirectToTheHomePageWhenThereIsNoSessionData(self):
        """
        Test that /confirm/ redirect to / when the session doesn,t
        contain any purchase data
        """
        self.assertRedirects(self.client.get('/confirm/'), '/')

    def test_itDisplaysTheContactName(self):
        """
        Test that the view displays the contact name
        """
        session = self.client.session
        session['invoice_id'] = self.invoice_id
        session.save()
        self.assertContains(self.client.get('/confirm/'), "Bruce Wayne" )
        self.assertContains(self.client.get('/confirm/'), "bruce@wayneenterprise.com" )
        self.assertContains(self.client.get('/confirm/'), "bruce@wayneenterprise.com" )

    def test_itDisplaysTheTotal(self):
        """
        Test that the view displays the total amount
        """
        session = self.client.session
        session['invoice_id'] = self.invoice_id
        session.save()
        self.assertContains(self.client.get('/confirm/'), "<b>Total:</b> 200 SEK" )

class TestPaypalView(TestCase):
    def test_2(self):
        self.client.get("/paypal/")
