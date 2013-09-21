from django.forms import ModelForm
from .models import TicketPurchase, Ticket
from django.forms.models import inlineformset_factory

class TicketPurchaseForm(ModelForm):
    class Meta:
        model = TicketPurchase

TicketFormSet = inlineformset_factory(TicketPurchase, Ticket)

