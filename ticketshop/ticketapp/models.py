from uuid import uuid4
from django.db import models
from django.core.exceptions import ValidationError
from coupons.models import Coupon
from django.core.mail import send_mail
from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged

# Create your models here.

class TicketType(models.Model):
    name  = models.CharField(max_length=200)
    description  = models.CharField(max_length=200)
    price = models.IntegerField()
    limit = models.IntegerField( null = True, blank = True )

    def __unicode__(self):
      return u"%s (%d:-)" % (self.name, self.price)

    def available(self, n=1):
        if self.limit is None:
            return True
        else:
            return self.ticket_set.count() + n <= self.limit
    class Meta:
        ordering = ['-price']

def default_ticket_type():
    Q = TicketType.objects.order_by('-price')
    if Q.count() > 0:
        return Q[0]
    else:
        return None

class Ticket(models.Model):
    name = models.CharField(max_length=200)
    ticket_type = models.ForeignKey(TicketType, default=default_ticket_type)
    purchase = models.ForeignKey("TicketPurchase", null = True, blank = True)

class TicketPurchase(models.Model):
    ## Contact details
    name = models.CharField(max_length=200)
    email = models.EmailField()
    keep_me_updated = models.BooleanField( default = False )
    additional_information = models.TextField( blank=True,
        help_text="Do not hesitate to let us know if you have specific requirements or comments about the registration.")
    ## Payment details
    coupon = models.ForeignKey(Coupon, null = True, blank = True)
    additional_contribution = models.IntegerField( default=0, blank=True,
        help_text = "We try to make the conference affordable for as many people as possible. Consider chipping in extra, if you can, to help keep it that way.")
    paid = models.BooleanField(default = False)
    ## Administrativia
    creation_date = models.DateTimeField(editable = False, auto_now_add = True)
    invoice_id = models.CharField(
                    max_length=36, default=uuid4, editable=False, unique=True)

    def price(self):
        p = 0
        for ticket in self.ticket_set.all():
            p += ticket.ticket_type.price
        p+= self.additional_contribution
        if self.coupon is not None:
            p = self.coupon.apply(p)
        return p

    def number_of_tickets(self):
        return self.ticket_set.count()


###############################################################################
# Payment handling
###############################################################################
class IPNHandler(object):
    NOTYFY_ADDRESS = "paypal@fscons.org"

    def __init__(self, sender=None, **kwargs):
        self.ERROR = None
        self.ipn = sender
        self.purchase = None
        try:
            self.purchase = Registration.objects.get( invoice_id = self.ipn.invoice)
            assert not self.registration.paid, "This ticket is already marked as paid..."
            assert self.ipn.payment_status == "Completed", \
                "Payment status is " + self.ipn.payment_status
            assert not self.ipn.flag, "IPN is flagged"
            assert self.registration.total() >= self.ipn.mc_gross, "Payment too low"
            self.registration.mark_as_paid()
            self.success()
        except Registration.DoesNotExist:
            self.fail("Couldn't find a matching registration object")
        except AssertionError, e:
            self.fail(str(e))
 
    def fail(self, error):
        self.ERROR = error
        mail = loader.get_template('registration_mail_ipn_fail.txt')
        send_mail(
            "[FSCONS'12][Paypal] IPN fail",
            mail.render(self._context({'error':error})),
            self.NOTYFY_ADDRESS,
            [self.NOTYFY_ADDRESS],
            fail_silently=False)
 
    def success(self):
        mail = loader.get_template('registration_mail_ipn_success.txt')
        send_mail(
            "[FSCONS'12][Paypal] IPN success",
            mail.render(self._context()),
            self.NOTYFY_ADDRESS,
            [self.NOTYFY_ADDRESS],
            fail_silently=False)
 
    def _context(self, params={}):
        defaults = {
            'registration': self.registration,
            'ipn': self.ipn,
            'site': Site.objects.get_current(),
            }
        defaults.update(params)
        return Context(defaults)
 
payment_was_successful.connect(IPNHandler)
payment_was_flagged.connect(IPNHandler)
