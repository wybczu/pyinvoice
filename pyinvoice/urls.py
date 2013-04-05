from django.conf.urls import patterns, include, url
import pyinvoice.views

urlpatterns = patterns(
    '',
    url(r'^$', pyinvoice.views.ListCompaniesView.as_view(), name='companies',),
    url(r'^invoices/(?P<company_id>\d)$', pyinvoice.views.ListInvoicesView.as_view(), name='invoices',),
)
