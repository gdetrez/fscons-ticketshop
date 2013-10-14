from django.dispatch import Signal
from .mails import send_confirmation_email


# ~~~ Custom signals ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
purchase_paid = Signal(providing_args=["purchase"])

# ~~~ Signal handlers ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def send_mail_on_paiement(sender, purchase, **kwargs):
    send_confirmation_email(purchase)
purchase_paid.connect(send_mail_on_paiement)
