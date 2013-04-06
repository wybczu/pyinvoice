#!/usr/bin/python
# -*- coding: utf8 -*-

from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from pyinvoice import models


class ListCompaniesView(ListView):

    model = models.Company


class ListInvoicesView(ListView):

    context_object_name = 'invoices'
    paginate_by = 12

    def get_queryset(self):
        self.company = get_object_or_404(models.Company, id=self.kwargs.get('company_id'))
        return models.Invoice.objects.filter(company=self.company).order_by('-date')
