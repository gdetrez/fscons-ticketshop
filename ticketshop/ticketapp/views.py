from functools import wraps
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models import Max, Min
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.edit import FormView

from paypal.standard.forms import PayPalPaymentsForm

from .forms import TicketPurchaseForm, TicketForm
from .models import TicketPurchase, TicketType, Ticket
from .utils import daterange


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
        "ticket_types": TicketType.objects.all(),
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
            "http://%s%s" % (site.domain, reverse('paypal-return')),
        "cancel_return":
            "http://%s%s" % (site.domain, reverse('confirm')),
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

@permission_required('ticketapp.view_report')
def report(request):
    data = {}
    # Total number of tickets
    tickets = Ticket.objects.filter(purchase__paid = True)
    data['ticket_total'] = tickets.count()
    # Tickets by type
    data['bytype'] = []
    for type_ in TicketType.objects.all():
        data['bytype'].append(
                ( unicode(type_),
                  tickets.filter( ticket_type = type_ ).count()
                ) )
    # By day
    data['by_day'] = []
    minmax = TicketPurchase.objects.aggregate(Max('creation_date'), Min('creation_date'))
    min_day = minmax['creation_date__min']
    max_day = minmax['creation_date__max']
    for day in daterange(min_day, max_day):
        # we want tickets created in this one day range
        drange = (day, day + timedelta( days = 1 ) )
        # counting the tickets
        count = tickets.filter( purchase__creation_date__range = drange ).count()
        data['by_day'].append( (day, count ) )
    return render_to_response("report.html", data)
