from django.forms import ModelForm
from django.forms import TextInput, Select
from .models import TicketPurchase, Ticket
from django.forms.models import inlineformset_factory

class TicketPurchaseForm(ModelForm):
    class Meta:
        model = TicketPurchase
        widgets = {
          'name': TextInput(attrs={'class':'form-control'}),
          'email': TextInput(attrs={'class':'form-control'}),
          }


class TicketForm(ModelForm):
    class Meta:
        model   = Ticket
        widgets = {
            'name':         TextInput(attrs={'class':'form-control', 'placeholder': 'Name on badge'}),
            'ticket_type':  Select(attrs={'class':'form-control'}),
        }

TicketFormSet = inlineformset_factory(TicketPurchase, Ticket,
    extra = 1,
    form=TicketForm)
