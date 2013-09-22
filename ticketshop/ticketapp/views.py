from django.views.generic.edit import FormView
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.forms.models import model_to_dict

from .forms import TicketPurchaseForm, TicketFormSet
from .models import TicketPurchase


def purchase_tickets(request):
    """
    This view displays the form to purchase tickets
    """
    form = TicketPurchaseForm()
    formset = TicketFormSet(instance=TicketPurchase())
    if request.POST:
        if 'plus' in request.POST:
            cp = request.POST.copy()
            cp['ticket_set-TOTAL_FORMS'] = int(cp['ticket_set-TOTAL_FORMS'])+ 1
            form = TicketPurchaseForm(cp)
            formset = TicketFormSet(cp, instance=TicketPurchase())
        elif 'minus' in request.POST:
            cp = request.POST.copy()
            cp['ticket_set-TOTAL_FORMS'] = max(1, int(cp['ticket_set-TOTAL_FORMS']) - 1)
            form = TicketPurchaseForm(cp)
            formset = TicketFormSet(cp, instance=TicketPurchase())
        else:
            form = TicketPurchaseForm(request.POST)
            if form.is_valid():
                purchase = form.save(commit=False)
                formset = TicketFormSet(request.POST, instance=purchase)
                if formset.is_valid():
                    #purchase.save()
                    request.session['ticket-purchase'] = purchase
                    request.session['tickets'] = formset.save(commit=False)
                    return HttpResponseRedirect('/confirm/')
            else:
                formset = TicketFormSet(request.POST, instance=TicketPurchase())
    elif 'ticket-purchase' in request.session:
        form = TicketPurchaseForm(instance=request.session['ticket-purchase'])
        tickets = [model_to_dict(t) for t in request.session['tickets']]
        print tickets
        formset = TicketFormSet(initial=tickets)
    return render_to_response("tickets/ticketpurchase_form.html", {
        "form": form,
        "formset": formset,
        }, context_instance=RequestContext(request))

def confirmation(request):
    """
    This view shows the user what she is about to buy
    """
    if 'ticket-purchase' in request.session:
        return render_to_response("tickets/confirm.html", {
            "details": request.session['ticket-purchase'],
            "tickets": request.session['tickets'],
            "total":   sum([ t.ticket_type.price for t in request.session['tickets']])
        }, context_instance=RequestContext(request))
    else:
        messages.error(request, 'Your session has expired.')
        messages.error(request, '')
        return redirect('/')
