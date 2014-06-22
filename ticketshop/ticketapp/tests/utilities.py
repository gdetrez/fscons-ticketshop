"""
Test utilities
"""
from datetime import date
from ..models import TicketType, Ticket, TicketPurchase, Coupon

def mkTicketPurchase(
        first_name="Mary",
        surname="Popins",
        email="mp@cloud.uk",
        tickets=[{'name':"Captain Haddock"}]):
    """
    Utility to create a new ticket purchase
    """
    purchase = TicketPurchase.objects.create(
            buyer_first_name=first_name,
            buyer_surname=surname,
            buyer_email=email,
    )
    for kwargs in tickets:
        purchase.tickets.create(**kwargs)
    return purchase

def mkTicketType(name="Test ticket", price=100, quantity=None):
    return TicketType.objects.create(
            name=name,
            price=price,
            quantity=quantity,
            description="This is a test ticket",
            sales_end=date.today()
    )


