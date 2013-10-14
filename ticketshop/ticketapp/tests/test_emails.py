import re

from django.test import TestCase
from django.core import mail

from ticketapp.models import TicketPurchase, TicketType


class ConfirmationEmailTest(TestCase):

    def setUp(self):
        """
        Create a purchase object and mark it as paid,
        which should trigger the sending of an email
        """
        t = TicketType.objects.create(
                name='Super hero ticket', price='1337' )
        p = TicketPurchase.objects.create(
                name="Batman", email="batman@gotham.gov" )
        p.ticket_set.create( name = "Batman", ticket_type = t )
        p.ticket_set.create( name = "Robin", ticket_type = t )
        p.mark_as_paid()

    def test_anEmailIsSend(self):
        """
        Test that an email has been send
        """
        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

    def test_subjectIs(self):
        """
        Email's subject should be 'Registration confirmation'
        """
        self.assertEqual("Registration confirmation", mail.outbox[0].subject)

    def test_fromEmail(self):
        """
        Email should be from 'FSCONS <info@fscons.org>'
        """
        self.assertEqual(
                "FSCONS <info@fscons.org>",
                mail.outbox[0].from_email)

    def test_toEmail(self):
        """
        Email should be to the purchase contact info
        """
        to = [ "Batman <batman@gotham.gov>" ]
        self.assertEqual( to, mail.outbox[0].recipients())

    def test_body(self):
        """
        Test email body
        """
        self.assertRegexpMatches( mail.outbox[0].body,
                re.compile( "Dear Batman,", flags=re.MULTILINE ) )
        self.assertRegexpMatches( mail.outbox[0].body,
                re.compile( "^Batman \(Super hero ticket\)", re.MULTILINE ) )
        self.assertRegexpMatches( mail.outbox[0].body,
                re.compile( "^Robin \(Super hero ticket\)", re.MULTILINE ) )
