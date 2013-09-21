from django.contrib import admin
from .models import TicketPurchase, Ticket, TicketType

class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1

class TicketPurchaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'number_of_tickets', 'price')
    inlines = [TicketInline]

admin.site.register(TicketPurchase, TicketPurchaseAdmin)
admin.site.register(TicketType)

