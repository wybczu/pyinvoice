#!/usr/bin/python
# -*- coding: utf8 -*-

from django.conf import settings
from pyinvoice import models
from django.core.files.base import ContentFile
import uuid
import time
import random
from urlparse import urljoin
import logging
import requests

logger = logging.getLogger(__name__)


class BaseScrapper(object):

    user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11'
    referer = None
    last_path = None  # domyslny referer
    base_url = None

    def __init__(self):
        self.session = requests.session()

    def _wait(self):
        if settings.RANDOMIZE_REQUEST_DELAY:
            delay = random.uniform(
                0.5 * settings.REQUEST_DELAY, 1.5 * settings.REQUEST_DELAY)
        else:
            delay = settings.REQUEST_DELAY
        time.sleep(delay)

    def _url(self, path):
        return urljoin(self.base_url, path)

    def get(self, path, *args, **kwargs):
        self._wait()
        return self.session.get(self._url(path), *args, **kwargs)

    def post(self, path, *args, **kwargs):
        self._wait()
        return self.session.post(self._url(path), *args, **kwargs)

    def create_invoice(self, invoice_number, total_gross, date=None):
        try:
            company = models.Company.objects.get(name=self.company_name)
        except models.Company.DoesNotExist:
            logger.info("New company: %s", self.company_name)
            company = models.Company(name=self.company_name)
            company.save()

        try:
            invoice = models.Invoice.objects.get(number=invoice_number)
            logger.info("Invoice %s already exists", invoice_number)
            invoice = None
        except models.Invoice.DoesNotExist:
            logger.info("New invoice: %s", invoice_number)
            invoice = models.Invoice()
            invoice.company = company
            invoice.number = invoice_number
            invoice.total_gross = total_gross
            if date is not None:
                invoice.date = date
            invoice.save()

        return invoice

    def save_document(self, invoice, data, title="Faktura"):
        document = models.Document()
        document.invoice = invoice
        document.title = title
        document.document_file.save(
            '%s.pdf' % uuid.uuid4(), ContentFile(data.content), save=True)
        document.save()
        logger.info("Downloaded file for invoice %s: %s (size: %s)", invoice.number, document.document_file.name, document.document_file.size)
