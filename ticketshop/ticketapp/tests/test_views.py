from django.test import Client
from django.contrib.auth.models import User
from django.contrib.messages.storage.base import Message
from django.contrib.messages.constants import ERROR

from django.test import TestCase
from ..models import TicketType, Ticket, TicketPurchase
from coupons.models import Coupon

class TicketPurchaseViewTest(TestCase):

    def test_getForm(self):
        """
        Test that we can get the purchase form
        """
        client = Client()
        self.assertContains(client.get("/"), "name")

class TestConfirmationView(TestCase):

    def setUp(self):
        # It appears that client.session only work
        # for non annonymous users
        self.client = Client()
        # Setup Test User
        User.objects.create_user('user', 'user@site.com', 'password')
        # Login
        self.client.login(username='user', password='password')

        # Create data
        TicketType.objects.create( name = "Standard ticket", price = 100 )

    def test_itRedirectToTheHomePageWhenThereIsNoSessionData(self):
        """
        Test that /confirm/ redirect to / when the session doesn,t
        contain any purchase data
        """
        self.assertRedirects(self.client.get('/confirm/'), '/')

    def test_itAddsAnErrorMessageWhenThereIsNoSessionData(self):
        """
        Test that /confirm/ adds an error message when the session doesn't
        contain any purchase data
        """
        response = self.client.get('/confirm/', follow=True)
        assert "Your session has expired." in [m.message for m in response.context.get('messages')]

    def test_itDisplaysTheContactName(self):
        """
        Test that the view displays the contact name
        """
        session = self.client.session
        session['ticket-purchase'] = \
            TicketPurchase( name = "Bruce Wayne",
                            email = "bruce@wayneenterprise.com")
        session['tickets'] = [
                Ticket( name = "Batman", ticket_type = TicketType.objects.get(name = "Standard ticket")),
                Ticket( name = "Catwoman", ticket_type = TicketType.objects.get(name = "Standard ticket")) ]
        session.save()
        self.assertContains(self.client.get('/confirm/'), "Bruce Wayne" )
        self.assertContains(self.client.get('/confirm/'), "bruce@wayneenterprise.com" )
        self.assertContains(self.client.get('/confirm/'), "bruce@wayneenterprise.com" )

    def test_itDisplaysTheTotal(self):
        """
        Test that the view displays the total amount
        """
        session = self.client.session
        session['ticket-purchase'] = \
            TicketPurchase( name = "Bruce Wayne",
                            email = "bruce@wayneenterprise.com")
        session['tickets'] = [
                Ticket( name = "Batman", ticket_type = TicketType.objects.get(name = "Standard ticket")),
                Ticket( name = "Catwoman", ticket_type = TicketType.objects.get(name = "Standard ticket")) ]
        session.save()
        self.assertContains(self.client.get('/confirm/'), "<b>Total:</b> 200 SEK" )

class TestPaypalView(TestCase):
    def test_2(self):
        client = Client()
        client.get("/paypal/")
