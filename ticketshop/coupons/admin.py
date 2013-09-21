from django.contrib import admin
from .models import Coupon


class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'percentage', 'active')

admin.site.register(Coupon, CouponAdmin)
