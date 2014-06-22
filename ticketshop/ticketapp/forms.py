import django.forms as forms
from django.core.exceptions import ValidationError
from .models import TicketPurchase, Ticket, TicketType

class TicketPurchaseForm(forms.ModelForm):
    class Meta:
        model = TicketPurchase
        fields = [
                'buyer_first_name', 'buyer_surname', 'buyer_email',
                'additional_information' ]

        widgets = {
          'buyer_first_name': forms.TextInput(attrs={'class':'form-control'}),
          'buyer_surname': forms.TextInput(attrs={'class':'form-control'}),
          'buyer_email': forms.TextInput(attrs={'class':'form-control'}),
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
        #self.fields['ticket_type'].queryset = TicketType.objects.available()

    class Meta:
        model  = Ticket
        fields = [
                'name',
                'email',
                'gender',
                'returning_visitor',
        ]
        widgets = {
            'name': forms.TextInput( attrs = {
                    'class':'form-control', 'placeholder': 'Name on badge'}),
            'email': forms.TextInput( attrs = {
                    'class':'form-control', 'placeholder': ''}),
            'gender': forms.Select( attrs={'class':'form-control'} ),
        }


class BaseTicketFormSet(forms.formsets.BaseFormSet):
    def __init__(self, *args, **kargs):
        self.instances = kargs['instances']
        del kargs['instances']
        super(BaseTicketFormSet, self).__init__(*args, **kargs)

    def _initial_form_count(self):
        return len(self.instances)

    def _construct_form(self, i, **kargs):
        kargs['instance'] = self.instances[i]
        kargs['empty_permitted'] = False
        return super(BaseTicketFormSet, self)._construct_form(i, **kargs)


TicketFormSet = forms.formsets.formset_factory(
        TicketForm,
        formset=BaseTicketFormSet,
        can_delete=False
)


class TicketsForm(forms.Form):
    """
    This is the first form: it shows all ticket types and allows the user
    to select how many ticket of each type are desired.
    """
    donation = forms.IntegerField(
            min_value=0,
            required=False,
            help_text=TicketPurchase._meta.get_field('additional_contribution').help_text
    )
    coupon   = forms.CharField(max_length=10, required=False)

    def __init__(self, ticket_types, valid_coupon_codes, *args, **kargs):
        """
        We extends the init method with two new parameters:
        - ticket_types is the list of ticket_types to show in the form
        - valid_coupon_codes is a list of valid coupon codes used in validation
        """
        super(TicketsForm, self).__init__(*args, **kargs)
        self.ticket_types = ticket_types
        for type_ in ticket_types:
            if type_.available():
                field = forms.IntegerField(
                        min_value=0,
                        max_value=10
                )
                self.fields['quantity:%s' % type_.id] = field

        def coupon_validator(c):
            if not c in valid_coupon_codes:
                raise ValidationError('Invalid coupon code')
        self.fields['coupon'].validators.append(coupon_validator)

