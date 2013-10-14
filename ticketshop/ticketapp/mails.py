"""
Using this file to add signal handlers because it is loaded automatically by
django
"""
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context


def send_confirmation_email(purchase):
    body = get_template('mails/confirmation.txt')
    d = Context({ 'purchase': purchase })

    send_mail(
        subject        = 'Registration confirmation',
        from_email     = 'FSCONS <info@fscons.org>',
        recipient_list = ['%s <%s>' % (purchase.name, purchase.email)],
        message        = body.render( d ),
        fail_silently  = False)
