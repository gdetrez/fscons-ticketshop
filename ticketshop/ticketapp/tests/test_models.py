# -*- coding: utf-8 -*-
"""
"""
from datetime import date
from django.test import TestCase
from ..models import TicketType, Ticket, TicketPurchase, Coupon

from .utilities import mkTicketType, mkTicketPurchase

class TicketTypeTest(TestCase):
    """
    Tests the TicketType model
    """

    def test_unicode(self):
        tt = mkTicketType()
        self.assertEqual(u"Test ticket", unicode(tt))

    def test_ticketWithoutLimitIsAvailable(self):
        tt = mkTicketType()
        self.assertTrue(tt.available())

    def test_ticketWithLimit0IsNotAvailable(self):
        tt = mkTicketType(quantity=0)
        self.assertFalse(tt.available())

    def test_nonSoldOutLimitedTicketIsAvailable(self):
        tt = mkTicketType(quantity=2)
        self.assertTrue(tt.available())

    def test_3TiketsAvailable(self):
        tt = mkTicketType(quantity=5)
        self.assertTrue(tt.available(3))

    def test_6TiketsNotAvailable(self):
        tt = mkTicketType(quantity=5)
        self.assertFalse(tt.available(6))

    def test_soldOutTicketNotAvailable(self):
        tt = mkTicketType(quantity=2)
        mkTicketPurchase(tickets=[
            {'name':"Professor Tournesol"},
            {'name':"Captain Haddock"},
        ])
        self.assertFalse(tt.available())

    def testCustomQueryset(self):
        """
        Test that the custom queryset works. It adds the available() method
        that returns only the tickets that are still available.

        To test it, we create 3 kind of tickets: one that is always available,
        one which has only 2 available and one that is unavailable.
        Calling TicketType.objects.available() at this point should return the
        first two.
        We then create tickets of the first two types and check again. Now
        TicketType.objects.available() should only return the first type.
        """
        available = TicketType.objects.create(
                name="Available ticket", price=1,
                sales_end=date.today())
        limited = TicketType.objects.create(
                name="Limited ticket", price=1, quantity=2,
                sales_end=date.today())
        unavailable = TicketType.objects.create(
                name="Unavailable ticket", price=1, quantity=0,
                sales_end=date.today())
        self.assertEqual([available, limited],
                [t for t in TicketType.objects.available().order_by( 'name' )]
            )
        mkTicketPurchase(tickets=[
            {'name': "...", 'ticket_type': available},
            {'name': "...", 'ticket_type': limited},
            {'name': "...", 'ticket_type': unavailable},
        ])
        self.assertEqual( [ available, limited ],
                [ t for t in TicketType.objects.available().order_by( 'name' ) ]
            )
        mkTicketPurchase(tickets=[
            {'name': "...", 'ticket_type': available},
            {'name': "...", 'ticket_type': limited},
            {'name': "...", 'ticket_type': unavailable},
        ])
        self.assertEqual( [ available ],
                [ t for t in TicketType.objects.available().order_by( 'name' ) ]
            )



class TicketTest(TestCase):

    def setUp(self):
        mkTicketType(name="Normal ticket", price=10)
        mkTicketType(name="Expensive ticket", price=1000)

    def test_defaultTicketType(self):
        t = Ticket(name="Johny")
        self.assertEqual("Expensive ticket", t.ticket_type.name)


class CouponModelTest(TestCase):

    def test_applyReduction(self):
        """
        Test the application of the percentage on a price
        """
        coupon = Coupon.objects.create( code = "ABC123", percentage = 20)
        self.assertEqual(80, coupon.apply(100))

    def test_unicode(self):
        """
        Test that the coupon's unicode is the same as the coupon code
        """
        coupon = Coupon.objects.create( code = u"ABC123", percentage = 10 )
        self.assertEqual(u"ABC123", unicode(coupon))


class TicketPurchaseTest(TestCase):

    def setUp(self):
        mkTicketType( name = "Expensive ticket", price = 100)
        mkTicketType( name = "Normal ticket", price = 10)
        mkTicketType( name = "Cheap ticket", price = 1)

    def test_unicode(self):
        p = mkTicketPurchase()
        self.assertEqual( unicode(p), u"Mary Popins (1 ticket(s))" )

    def test_canCreatePurchase(self):
        p = mkTicketPurchase()
        p.tickets.create( name = "Mary Popins",
            ticket_type = TicketType.objects.get(name = "Normal ticket"))
        self.assertEqual( p, TicketPurchase.objects.get( id = 1))

    def test_computePrice(self):
        p = mkTicketPurchase(tickets=[])
        p.tickets.create( name = "Mary Popins",
            ticket_type = TicketType.objects.get(name = "Normal ticket"))
        p.tickets.create( name = "Bert",
            ticket_type = TicketType.objects.get(name = "Cheap ticket"))
        p.tickets.create( name = "George Banks",
            ticket_type = TicketType.objects.get(name = "Expensive ticket"))
        self.assertEqual( 111, p.price())

    def test_coupon(self):
        coupon = Coupon.objects.create( code = "123AOE", percentage = 10)
        p = mkTicketPurchase(tickets=[])
        p.tickets.create( name = "George Banks",
            ticket_type = TicketType.objects.get(name = "Expensive ticket"))
        p.coupon = coupon
        self.assertEqual( 90, p.price())

    def test_numberOfTickets(self):
        p = mkTicketPurchase(tickets=[])
        self.assertEquals(0, p.number_of_tickets())
        p.tickets.create( name = "Mary Popins",
            ticket_type = TicketType.objects.get(name = "Normal ticket"))
        self.assertEquals(1, p.number_of_tickets())
        p.tickets.create( name = "Bert",
            ticket_type = TicketType.objects.get(name = "Cheap ticket"))
        p.tickets.create( name = "George Banks",
            ticket_type = TicketType.objects.get(name = "Expensive ticket"))
        self.assertEquals(3, p.number_of_tickets())


from ..models import purchase_paid
from mock import Mock, ANY
class PaymentReceivedSignalTest(TestCase):

    def test_markingATicketPurchaseAsPaidSendTheSignal(self):
        receiver = Mock()
        purchase_paid.connect(receiver)
        mkTicketType()
        p = mkTicketPurchase()
        p.mark_as_paid()
        receiver.assert_called_once_with(sender=ANY, purchase=p, signal=ANY)
