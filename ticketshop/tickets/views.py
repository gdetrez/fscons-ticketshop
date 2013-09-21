from django.views.generic.edit import FormView
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
#from recipes.models import Recipe, RecipeIngredient
from .forms import TicketPurchaseForm, TicketFormSet
from .models import TicketPurchase


def purchase_tickets(request):
    """
    This view displays the form to purchase tickets
    """
    if request.POST:
        form = TicketPurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            tickets = TicketFormSet(request.POST, instance=purchase)
            if tickets.is_valid():
                purchase.save()
                tickets.save()
                #return HttpResponseRedirect(reverse('recipes_submit_posted'))
    else:
        form = TicketPurchaseForm()
        tickets = TicketFormSet(instance=TicketPurchase())
    return render_to_response("tickets/ticketpurchase_form.html", {
        "form": form,
        "tickets": tickets,
        }, context_instance=RequestContext(request))
