# Create your views here.

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from pyinvoice import models


def companies(request, template_name='companies.html'):
    return render_to_response(template_name,
           {
               'companies': models.Company.objects.all(),
           },
           context_instance=RequestContext(request))


def invoices(request, company_id=None, template_name='invoices.html'):
    company = get_object_or_404(models.Company, id=company_id)
    request.breadcrumbs(company.name, request.path)
    return render_to_response(template_name,
           {
               'invoices': company.invoice_set.all(),
           },
           context_instance=RequestContext(request))


def invoice_details(request, invoice_id=None, template_name='invoice_details.html'):
    invoice = get_object_or_404(models.Invoice, id=invoice_id)
    request.breadcrumbs(
        (invoice.company.name, reverse('invoices', args=[invoice.company.id])), 
        ('Faktura ' + invoice.number, request.path)
    )
    return render_to_response(template_name,
           {
               'invoice': invoice,
           },
           context_instance=RequestContext(request))

