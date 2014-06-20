from django.contrib import admin
from django.contrib import messages

from .models import TicketPurchase, Ticket, TicketType, Coupon
from .mails import send_confirmation_email

# ~~~ Ticket purchase ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TicketInline(admin.TabularInline):
    """
    This is used to displayed the purchased ticket inline in the
    page showing the details of a single purchase
    """
    model = Ticket
    extra = 1

def mark_selected_paid(modeladmin, request, queryset):
    """
    Custom action that marks a bunch of tickets as paid
    using the mark_as_paid function that takes care of
    sending the cenfirmation email
    """
    for purchase in queryset:
        purchase.mark_as_paid()
mark_selected_paid.short_description = "Mark selected as paid"


def resend_confirmation(modeladmin, request, queryset):
    """
    Custom admin action that re-send a confirmation email for the selected
    purchases. Note that the purchases need to be marked as paid otherwise
    the action will silently skip them
    """
    for purchase in queryset:
        if purchase.paid:
            send_confirmation_email(purchase)
        else:
            messages.warning(request, "Skiped unpaid purchase: %s. Use \"Mark selected as paid instead\"" % purchase)
resend_confirmation.short_description = "Re-send confirmation email"

class TicketPurchaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'number_of_tickets', 'price', 'invoice_id', 'paid')
    date_hierarchy = 'creation_date'
    inlines = [TicketInline]
    list_filter = ['paid','coupon', 'ticket__ticket_type']
    search_fields = ['name', 'email', 'additional_information', 'invoice_id', 'ticket__name']
    actions = [mark_selected_paid, resend_confirmation]


admin.site.register(TicketPurchase, TicketPurchaseAdmin)
admin.site.register(TicketType)

class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'percentage', 'active')

admin.site.register(Coupon, CouponAdmin)
