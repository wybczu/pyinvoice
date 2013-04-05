# Create your views here.

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from pyinvoice import models
from django.views.generic import ListView


class ListCompaniesView(ListView):

    model = models.Company


class ListInvoicesView(ListView):

    context_object_name = 'invoices'
    paginate_by = 12

    def get_queryset(self):
        self.company = get_object_or_404(models.Company, id=self.kwargs.get('company_id'))
        return models.Invoice.objects.filter(company=self.company).order_by('-date')
