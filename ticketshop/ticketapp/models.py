# -*- coding: utf-8 -*-
from uuid import uuid4

from django.db import models
from django.db.models import Count, Q, F
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, mail_admins
from django.dispatch import Signal

from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged

from .mails import send_confirmation_email


class TicketTypeManager(models.Manager):
    """
    Create a custom manager with an extra method
    that only returns available ticket types
    """
    def available(self):
        """
        Custom method that return a queryset with only
        available tickets
        """
        return super(TicketTypeManager, self).get_query_set() \
            .annotate( num_sold = Count('ticket') ) \
            .filter(Q(quantity=None) | Q(num_sold__lt=F('quantity')))

class TicketType(models.Model):
    """
    A type of ticket is for instance "regular", "early bird", etc.

    """
    name  = models.CharField(max_length=200,
            help_text="How do you call this kind of ticket? E.g. \"Early bird\" or \"Student\"")
    description  = models.TextField(blank=True,
            help_text="What does this ticket gives access to and who can by it.")
    price = models.IntegerField(
            help_text="Price in SEK.")
    sales_end = models.DateField(
            help_text="After this, it won't be possible to buy this ticket anymore.")
    quantity = models.IntegerField( null = True, blank = True,
            help_text="Maximum number of ticket of this type.")

    # Add our custom manager
    objects = TicketTypeManager()

    def __unicode__(self):
      return u"%s" % (self.name)

    def available(self, n=1):
        if self.quantity is None:
            return True
        else:
            return self.ticket_set.count() + n <= self.quantity
    class Meta:
        ordering = ['-price']

def default_ticket_type():
    Q = TicketType.objects.order_by('-price')
    if Q.count() > 0:
        return Q[0]
    else:
        return None

class Ticket(models.Model):
    ticket_type = models.ForeignKey(TicketType, default=default_ticket_type)
    name = models.CharField(max_length=200,
            help_text="This is the name that will be printed on your badge")
    email = models.EmailField()
    # Gender distribution, as required by the manifesto.
    # For a discussion on more inclusive gender question, see
    # http://itspronouncedmetrosexual.com/2012/06/how-can-i-make-the-gender-question-on-an-application-form-more-inclusive/
    gender = models.CharField(max_length=1,
            verbose_name="I identify my gender as…",
            help_text="Why are we asking this? We ask you for your gender in order to evaluate our effort in reaching a fair and reasonable, within 60/40, gender distribution among participants.",
            choices = (
                ('F', 'Women'),
                ('M', 'Men'),
                ('T', 'Trans*'),
                ('?', 'Prefer not to disclose')
    ))
    returning_visitor = models.BooleanField(
            verbose_name="I have been to FSCONS before",
    )
    purchase = models.ForeignKey("TicketPurchase", related_name="tickets")
    class Meta:
      permissions = ( ("view_reportk", "Can see the ticket report"), )

class Coupon(models.Model):
    code = models.CharField( max_length = 10, primary_key=True )
    percentage = models.IntegerField()
    active = models.BooleanField( default = True )

    def apply(self, price):
        return price * (100 - self.percentage) / 100

    def __unicode__(self):
        return unicode(self.code)

class TicketPurchase(models.Model):
    ## Contact details
    buyer_first_name = models.CharField(
            verbose_name="First name",
            max_length=200)
    buyer_surname = models.CharField(
            verbose_name="Surname",
            max_length=200)
    buyer_email = models.EmailField(
            verbose_name="E-mail")
    additional_information = models.TextField( blank=True,
        help_text="Do not hesitate to let us know if you have specific requirements or comments about the registration.")
    ## Payment details
    coupon = models.ForeignKey(Coupon, null = True, blank = True,
            help_text="If you have a promotional code, enter it here:")
    additional_contribution = models.IntegerField( default=0, blank=True,
            help_text = "We try to make the conference affordable for as many people as possible. Consider chipping in extra, if you can, to help keep it that way.")
    paid = models.BooleanField(default = False, editable = False)
    ## Administrativia
    creation_date = models.DateTimeField(editable = False, auto_now_add = True)
    invoice_id = models.CharField(
                    max_length=36, default=uuid4, editable=False, unique=True)

    def __unicode__(self):
        return u"%s %s (%d ticket(s))" % (
                self.buyer_first_name,
                self.buyer_surname,
                self.number_of_tickets())

    def price(self):
        p = 0
        for ticket in self.tickets.all():
            p += ticket.ticket_type.price
        p+= self.additional_contribution
        if self.coupon is not None:
            p = self.coupon.apply(p)
        return p

    def number_of_tickets(self):
        return self.tickets.count()

    def mark_as_paid(self):
        """
        Mark an unpaid purchase as paid and send a purchase_paid signal
        """
        if not self.paid:
            self.paid = True
            self.save( update_fields=['paid'] )
            purchase_paid.send(sender=self, purchase=self)


# ~~~ Custom signals ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
purchase_paid = Signal(providing_args=["purchase"])

# ~~~ Signal handlers ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def send_mail_on_paiement(sender, purchase, **kwargs):
    send_confirmation_email(purchase)
purchase_paid.connect(send_mail_on_paiement)

# ~~~ Payment handling
class IPNHandler(object):
    import logging
    log = logging.getLogger("IPN handler")

    def __init__(self, sender=None, **kwargs):
        self.ERROR = None
        self.ipn = sender
        purchase = TicketPurchase.objects.get( invoice_id = self.ipn.invoice)
        if self.ipn.test_ipn:
          return
        #assert not purchase.paid, "This ticket is already marked as paid..."
        assert self.ipn.payment_status == "Completed", \
            "Payment status is " + self.ipn.payment_status
        assert purchase.price() <= self.ipn.mc_gross, "Wrong amount: %f instead of %d" % (self.ipn.mc_gross, purchase.price())
        purchase.mark_as_paid()
        self.log.info("TicketPurchase %i paid with paypal" % purchase.pk )

payment_was_successful.connect(IPNHandler)

def alert_flagged_payment(sender,**kwargs):
    mail_admins("Flagged IPN",
      "Paypal IPN has been flagged.\n" + \
      "https://tickets.fscons.org/admin/ipn/paypalipn/%d/\n" % sender.pk + \
      "https://tickets.fscons.org/admin/ticketapp/ticketpurchase/?q=%s\n" % sender.invoice
      )
payment_was_flagged.connect(alert_flagged_payment)
