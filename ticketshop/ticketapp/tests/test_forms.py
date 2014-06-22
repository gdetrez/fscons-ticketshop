from django.test import TestCase
from ..models import TicketType
from ..forms import TicketsForm
from .utilities import mkTicketType

#class TicketFormTest(TestCase):
#    """
#    Tests the TicketForm
#    """
#    def testFormOffersOnlyAvailableTicketTypes(self):
#        """
#        Test that the choices for the ticket_type field only lists
#        available ticket types
#        """
#        available = TicketType.objects.create( name = "Available", price = 1 )
#        TicketType.objects.create( name = "Unavailable", price = 1, limit = 0 )
#        form = TicketForm()
#        self.assertEqual( 1, form.fields['ticket_type'].queryset.count() )
#        self.assertEqual( [available], list(form.fields['ticket_type'].queryset))

class TicketsFormTest(TestCase):

    def assertValid(self, form):
        self.assertTrue(form.is_valid())

    def assertInvalid(self, form):
        self.assertFalse(form.is_valid())

    def test_valid_data(self):
        tt = mkTicketType()
        form = TicketsForm([tt], [], {'quantity:1':0, 'donation':0})
        self.assertValid(form)

    def test_negative_donation(self):
        form = TicketsForm([],[], {'donation':'-50'})
        self.assertInvalid(form)

    def test_invalid_coupon(self):
        form = TicketsForm([], ["VALID"], {'donation':0, 'coupon': "INVALID"})
        self.assertInvalid(form)

    def test_valid_coupon(self):
        form = TicketsForm([], ["COUPON"], {'donation':0, 'coupon': "COUPON"})
        self.assertValid(form)

    def test_tryToBuyASoldoutTicket(self):
        tt = mkTicketType(quantity=0)
        form = TicketsForm([tt], [], {'donation':0, 'quantity:%d' % tt.id:'1'})
        form.is_valid()
        self.assertFalse(form.cleaned_data.has_key('quantity:1'))

    def test_tryToBuyTooManyTickets(self):
        tt = mkTicketType()
        form = TicketsForm([tt],[],{'donation':0, 'quantity:%d'%tt.id:'100'})
        self.assertInvalid(form)
