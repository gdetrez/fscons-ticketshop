"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from ..models import Coupon

class CouponModelTest(TestCase):
    def test_can_create(self):
        """
        Test that we can create coupons
        """
        Coupon.objects.create( code = "ABC123", percentage = 20)

    def test_applyReduction(self):
        """
        Test the application of the percentage on a price
        """
        coupon = Coupon.objects.create( code = "ABC123", percentage = 20)
        self.assertEqual(80, coupon.apply(100))

    def test_unicode(self):
        """
        Test that the coupon's unicode is the same as the coupon code
        """
        coupon = Coupon.objects.create( code = u"ABC123", percentage = 10 )
        self.assertEqual(u"ABC123", unicode(coupon))
