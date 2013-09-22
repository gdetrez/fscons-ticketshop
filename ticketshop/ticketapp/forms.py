from django.forms import ModelForm
from django.forms import TextInput, Select, Textarea
from .models import TicketPurchase, Ticket
from django.forms.models import inlineformset_factory

class TicketPurchaseForm(ModelForm):
    class Meta:
        model = TicketPurchase
        widgets = {
          'name': TextInput(attrs={'class':'form-control'}),
          'email': TextInput(attrs={'class':'form-control'}),
          'coupon': TextInput(attrs={'class':'form-control'}),
          'additional_information': Textarea(attrs={'class':'form-control'}),
          'additional_contribution': TextInput(attrs={'class':'form-control col-lg-3'}),
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
