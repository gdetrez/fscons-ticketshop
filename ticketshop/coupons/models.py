from django.db import models

# Create your models here.
class Coupon(models.Model):
    code = models.CharField( max_length = 10, primary_key=True )
    percentage = models.IntegerField()
    active = models.BooleanField( default = True )

    def apply(self, price):
        return price * (100 - self.percentage) / 100

    def __unicode__(self):
        return unicode(self.code)
