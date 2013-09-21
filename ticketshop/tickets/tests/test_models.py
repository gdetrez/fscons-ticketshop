"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from ..models import TicketType, Ticket, TicketPurchase
from coupons.models import Coupon

class TicketTypeTest(TestCase):

    def test_canCreateTicketType(self):
        """
        Test that we can create and save a TicketType object
        """
        tt = TicketType( name = "Business ticket", price = 2000)
        tt.save()
        self.assertEqual(tt, TicketType.objects.get(id = 1))

    def test_unicode(self):
        tt = TicketType( name = "Test Ticket", price = 30,
            description = "This is a test ticket")
        self.assertEqual(u"Test Ticket (30:-)", unicode(tt))

    def test_ticketWithoutLimitIsAvailable(self):
        tt = TicketType( name = "Test Ticket", price = 30,
            description = "This is a test ticket")
        self.assertTrue(tt.available())

    def test_ticketWithLimit0IsNotAvailable(self):
        tt = TicketType( name = "Ghost ticket", price = 1, limit = 0 )
        self.assertFalse(tt.available())

    def test_nonSoldOutLimitedTicketIsAvailable(self):
        tt = TicketType( name = "limited ticket", price = 10, limit = 2)
        self.assertTrue(tt.available())

    def test_3TiketsAvailable(self):
        tt = TicketType( name = "limited ticket", price = 10, limit = 5)
        self.assertTrue(tt.available(3))

    def test_6TiketsNotAvailable(self):
        tt = TicketType( name = "limited ticket", price = 10, limit = 5)
        self.assertFalse(tt.available(6))

    def test_soldOutTicketNotAvailable(self):
        tt = TicketType( price = 1, limit = 2 )
        tt.save()
        Ticket( name = "Professor Tournesol", ticket_type = tt).save()
        Ticket( name = "Captain Haddock", ticket_type = tt).save()
        self.assertFalse(tt.available())

class TicketTest(TestCase):

    def setUp(self):
        self.tt = TicketType( name = "Normal ticket", price = 10)
        self.tt.save()

    def test_canCreateAndSave(self):
        t = Ticket( name = "Johny", ticket_type = self.tt )
        t.save()

class TicketPurchaseTest(TestCase):

    def setUp(self):
        TicketType( name = "Expensive ticket", price = 100).save()
        TicketType( name = "Normal ticket", price = 10).save()
        TicketType( name = "Cheap ticket", price = 1).save()

    def test_canCreatePurchase(self):
        p = TicketPurchase.objects.create(
            name = "Mary Popins", email = "mp@clouds.org")
        p.ticket_set.create( name = "Mary Popins",
            ticket_type = TicketType.objects.get(name = "Normal ticket"))
        self.assertEqual( p, TicketPurchase.objects.get( id = 1))

    def test_computePrice(self):
        p = TicketPurchase.objects.create(
            name = "Mary Popins", email = "mp@clouds.org")
        p.ticket_set.create( name = "Mary Popins",
            ticket_type = TicketType.objects.get(name = "Normal ticket"))
        p.ticket_set.create( name = "Bert",
            ticket_type = TicketType.objects.get(name = "Cheap ticket"))
        p.ticket_set.create( name = "George Banks",
            ticket_type = TicketType.objects.get(name = "Expensive ticket"))
        self.assertEqual( 111, p.price())

    def test_coupon(self):
        coupon = Coupon.objects.create( code = "123AOE", percentage = 10)
        p = TicketPurchase.objects.create(
            name = "Mary Popins", email = "mp@clouds.org")
        p.ticket_set.create( name = "George Banks",
            ticket_type = TicketType.objects.get(name = "Expensive ticket"))
        p.coupon = coupon
        self.assertEqual( 90, p.price())

    def test_numberOfTickets(self):
        p = p = TicketPurchase.objects.create(
            name = "Mary Popins", email = "mp@clouds.org")
        self.assertEquals(0, p.number_of_tickets())
        p.ticket_set.create( name = "Mary Popins",
            ticket_type = TicketType.objects.get(name = "Normal ticket"))
        self.assertEquals(1, p.number_of_tickets())
        p.ticket_set.create( name = "Bert",
            ticket_type = TicketType.objects.get(name = "Cheap ticket"))
        p.ticket_set.create( name = "George Banks",
            ticket_type = TicketType.objects.get(name = "Expensive ticket"))
        self.assertEquals(3, p.number_of_tickets())
