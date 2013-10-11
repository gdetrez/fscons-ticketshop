import django.dispatch

purchase_paid = django.dispatch.Signal(providing_args=["purchase"])

