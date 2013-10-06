from django.views.generic.edit import FormView
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.forms.models import model_to_dict
from django.contrib.sites.models import Site
from functools import wraps
from paypal.standard.forms import PayPalPaymentsForm

from .forms import TicketPurchaseForm, TicketForm
from .models import TicketPurchase


def purchase_tickets(request):
    """
    This view displays the form to purchase tickets
    """
    if request.POST:
        form = TicketPurchaseForm(request.POST)
        n = int(request.POST['ticket_count']) # Number of ticket.
        ticket_forms = [TicketForm( request.POST, prefix="ticket%d" % i )
                          for i in range(n) ]
        if 'plus' in request.POST:
            ticket_forms.append(
                    TicketForm( prefix="ticket%d" % len(ticket_forms) ) )
        elif 'minus' in request.POST:
            if len(ticket_forms) > 1: ticket_forms.pop()
            else: messages.warning(request, 'Your have to buy at least one ticket.')
        elif form.is_valid() and all( tf.is_valid() for tf in ticket_forms ):
            purchase = form.save()
            print ticket_forms
            for tf in ticket_forms:
                ticket = tf.save( commit = False )
                ticket.purchase = purchase
                ticket.save()
                print "ticket saved: %s" % ticket
            request.session['invoice_id'] = purchase.invoice_id
            return HttpResponseRedirect('/confirm/')

    else:
        form = TicketPurchaseForm()
        ticket_forms = [ TicketForm( prefix = "ticket0" ) ] # By default, 1 ticket
    return render_to_response("form.html", {
        "form": form,
        "ticket_forms": ticket_forms,
        }, context_instance=RequestContext(request))


def purchase_required(view):
    """
    This is a decorator that indicates that a view
    requires a purchase to be in progress to work.
    """
    def _decorator(request, *args, **kwargs):
        if 'invoice_id' in request.session:
            purchase = TicketPurchase.objects.get( invoice_id = request.session['invoice_id'])
            return view(request, purchase, *args, **kwargs)
        else:
            messages.error(request, 'Your session has expired.') 
            return redirect('/')
    return wraps(view)(_decorator)

@purchase_required
def confirmation(request, purchase):
    """
    This view shows the user what she is about to buy
    """
    # Create the paypal url to redirect the user.
    # This a a bit convoluted because the django app that we use to handle
    # PayPal payments only generates POST forms to send the user to paypal.
    # So we have to convert the form to a query string
    site = Site.objects.get_current()
    paypal_dict = {
        "business": "paypal@fscons.org",
        "amount": purchase.price,
        "currency_code": "SEK",
        "item_name": "FSCONS 2013 tickets",
        "invoice": purchase.invoice_id,
        "notify_url":
            "http://%s%s" % (site.domain, reverse('paypal-ipn')),
        "return_url":
            "http://%s%s" % (site.domain, reverse('paypal-success')),
        "cancel_return":
            "http://%s%s" % (site.domain, reverse('paypal-cancel')),
        }
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render_to_response("confirm.html", {
        "purchase": purchase,
        "paypal": form,
    }, context_instance=RequestContext(request))

def success(self):
    pass
def cancel(request):
    pass

