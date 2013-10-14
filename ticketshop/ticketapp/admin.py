from django.contrib import admin
from .models import TicketPurchase, Ticket, TicketType, Coupon

class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1

def mark_selected_paid(modeladmin, request, queryset):
    for purchase in queryset:
        purchase.mark_as_paid()
mark_selected_paid.short_description = "Mark selected stories as paid"


class TicketPurchaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'number_of_tickets', 'price', 'invoice_id', 'paid')
    date_hierarchy = 'creation_date'
    inlines = [TicketInline]
    list_editable = ('paid',)
    list_filter = ['paid','coupon', 'ticket__ticket_type']
    search_fields = ['name', 'email', 'additional_information', 'invoice_id']
    actions = [mark_selected_paid]


admin.site.register(TicketPurchase, TicketPurchaseAdmin)
admin.site.register(TicketType)

class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'percentage', 'active')

admin.site.register(Coupon, CouponAdmin)
