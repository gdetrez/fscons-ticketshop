from django.test import Client

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
