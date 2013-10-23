import django.forms as forms
from .models import TicketPurchase, Ticket, TicketType

class TicketPurchaseForm(forms.ModelForm):
    class Meta:
        model = TicketPurchase
        widgets = {
          'name': forms.TextInput(attrs={'class':'form-control'}),
          'email': forms.TextInput(attrs={'class':'form-control'}),
          'coupon': forms.TextInput(attrs={'class':'form-control'}),
          'additional_information': forms.Textarea(attrs={'class':'form-control', 'rows': 2}),
          'additional_contribution': forms.TextInput(attrs={'class':'form-control col-lg-3'}),
          }


class TicketForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        """
        We extends the __init__ method to be able to restrict
        ticket types to available types by overwriting the queryset
        """
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['ticket_type'].queryset = TicketType.objects.available()

    class Meta:
        model  = Ticket
        exclude = ('purchase',)
        widgets = {
            'ticket_type': forms.Select( attrs={'class':'form-control'} ),
            'name': forms.TextInput( attrs = {
                    'class':'form-control', 'placeholder': 'Name on badge'})}
