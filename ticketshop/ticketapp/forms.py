import django.forms as forms
from django.forms import ModelForm, ValidationError
from django.forms import TextInput, Select, Textarea
from .models import TicketPurchase, Ticket
from django.forms.formsets import formset_factory, BaseFormSet

class TicketPurchaseForm(ModelForm):
    class Meta:
        model = TicketPurchase
        widgets = {
          'name': TextInput(attrs={'class':'form-control'}),
          'email': TextInput(attrs={'class':'form-control'}),
          'coupon': TextInput(attrs={'class':'form-control'}),
          'additional_information': Textarea(attrs={'class':'form-control', 'rows': 2}),
          'additional_contribution': TextInput(attrs={'class':'form-control col-lg-3'}),
          }


class TicketForm(forms.ModelForm):
    class Meta:
        model  = Ticket
        exclude = ('purchase',)
        widgets = {
                'ticket_type': forms.Select(attrs={'class':'form-control'}),
                'name': forms.TextInput( attrs = {
                        'class':'form-control', 'placeholder': 'Name on badge'})}

# We subclass the BaseInlineFormSet to add a validity condition:
# There should be at least one element (ticket) in the set
class BaseTicketFormSet(BaseFormSet):
    def clean(self):
        """Check that there is at least one ticket"""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        if len(self.forms) < 1:
            raise ValidationError("You have to buy at least one ticket!")

    def initial_form_count(self):
        return 1


TicketFormSet = formset_factory(TicketForm,
    formset=BaseTicketFormSet,
    extra = 0,
    can_delete=False)
