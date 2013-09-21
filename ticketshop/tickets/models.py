from django.db import models
from django.core.exceptions import ValidationError
from coupons.models import Coupon

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

class Ticket(models.Model):
    name = models.CharField(max_length=200)
    ticket_type = models.ForeignKey(TicketType)
    purchase = models.ForeignKey("TicketPurchase", null = True, blank = True)

class TicketPurchase(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    coupon = models.ForeignKey(Coupon, null = True, blank = True)

    def price(self):
        p = 0
        for ticket in self.ticket_set.all():
            p += ticket.ticket_type.price
        if self.coupon is not None:
            p = self.coupon.apply(p)
        return p

    def number_of_tickets(self):
        return self.ticket_set.count()
