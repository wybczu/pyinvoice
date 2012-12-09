from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^$',
                           'pyinvoice.views.companies', name='companies'),
                       url(
                       r'^invoices/(?P<company_id>\d)$', 'pyinvoice.views.invoices',
                       name='invoices'),
                       url(r'^invoice_details/(?P<invoice_id>\d)$',
                           'pyinvoice.views.invoice_details', name='invoice_details'),
                       )
