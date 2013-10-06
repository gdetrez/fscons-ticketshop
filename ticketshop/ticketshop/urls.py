from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from ticketapp.views import purchase_tickets, confirmation, success, cancel
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', purchase_tickets),
    url(r'^confirm/$', confirmation),
    url(r'^success/$',
            TemplateView.as_view(template_name="paypal_return.html"),
            name='paypal-return'),
    url(r'^cancel/$',
            TemplateView.as_view(template_name="paypal_cancel.html"),
            name='paypal-cancel'),
    url(r'^api/paypal/bofasdflkjsdf/', include('paypal.standard.ipn.urls'), name="paypal-ipn"),

    # Examples:
    # url(r'^$', 'ticketshop.views.home', name='home'),
    # url(r'^ticketshop/', include('ticketshop.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
