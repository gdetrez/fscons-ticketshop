from django.test import TestCase
from ..models import TicketType
from ..forms import TicketForm

class TicketFormTest(TestCase):
    """
    Tests the TicketForm
    """
    def testFormOffersOnlyAvailableTicketTypes(self):
        """
        Test that the choices for the ticket_type field only lists
        available ticket types
        """
        available = TicketType.objects.create( name = "Available", price = 1 )
        TicketType.objects.create( name = "Unavailable", price = 1, limit = 0 )
        form = TicketForm()
        self.assertEqual( 1, form.fields['ticket_type'].queryset.count() )
        self.assertEqual( [available], list(form.fields['ticket_type'].queryset))
