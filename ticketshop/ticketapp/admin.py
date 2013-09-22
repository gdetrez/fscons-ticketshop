from django.contrib import admin
from .models import TicketPurchase, Ticket, TicketType, Coupon

class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1

class TicketPurchaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'number_of_tickets', 'price', 'paid')
    date_hierarchy = 'creation_date'
    inlines = [TicketInline]
    list_editable = ('paid',)
    list_filter = ['paid','coupon', 'ticket__ticket_type']
    search_fields = ['name', 'email', 'additional_information', '']

admin.site.register(TicketPurchase, TicketPurchaseAdmin)
admin.site.register(TicketType)

class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'percentage', 'active')

admin.site.register(Coupon, CouponAdmin)
