"""donation_portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from donation.views.accounting import accounting_reconciliation, donation_counter
from donation.views.donations import PledgeView, download_receipt
from donation.views.export import render_export_page, download_spreadsheet, download_full_spreadsheet

urlpatterns = [
    # Accounting
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounting_reconciliation', accounting_reconciliation, name='accounting-reconciliation'),
    url(r'^secret_donation_counter', donation_counter, name='donation-counter'),
    # Data export
    url(r'^export', render_export_page, name='export-page'),
    url(r'^download_full_spreadsheet', download_full_spreadsheet, name='download-full-spreadsheet'),
    url(r'^download_spreadsheet', download_spreadsheet, name='download-spreadsheet'),
    # Donations
    # url(r'^pledge/([0-9])/$', pledge, name='pledge')
    url(r'^pledge$', PledgeView.as_view(), name='pledge'),
    url(r'^pledge2', PledgeView.as_view(), kwargs={'template_name': "pledge-reactive.html"}, name='pledge2'),
    url(r'^receipt/(?P<pk>[0-9]+)/(?P<secret>[a-zA-Z0-9]+)', download_receipt, name='download-receipt'),
    url(r'^paypal/', include('paypal.standard.ipn.urls')),
]

urlpatterns += staticfiles_urlpatterns()

urlpatterns.append(url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))
