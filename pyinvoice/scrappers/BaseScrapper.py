#!/usr/bin/python
# -*- coding: utf8 -*-

from django.conf import settings
from pyinvoice import  models
from django.core.files.base import ContentFile
import uuid
from lxml import etree
import cookielib, urllib2, urllib
import time, random
from urlparse import urljoin
import logging

logger = logging.getLogger(__name__)

class BaseScrapper(object):

    user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11'
    referer = None
    last_path = None # domyslny referer
    base_url = None
    
    def __init__(self):
        self.cookie_jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
    
    def get(self, path, params = None, referer = None, headers = None):
        if settings.RANDOMIZE_REQUEST_DELAY:
            delay = random.uniform(0.5*settings.REQUEST_DELAY, 1.5*settings.REQUEST_DELAY) 
        else:
            delay = settings.REQUEST_DELAY 
        time.sleep(delay)

        if referer is not None:
            self.referer = urljoin(self.base_url, referer)
        if self.last_path is not None:
            self.referer = urljoin(self.base_url, self.last_path)
        self.opener.addheaders = [
            ('User-Agent', self.user_agent),
        ]
        if headers is not None:
            for header in headers: self.opener.addheaders.append(header)
        if self.referer is not None:
            self.opener.addheaders.append(('Referer', urljoin(self.base_url, self.referer)))
    	self.last_path = path
        data = None
        if params is not None:
            if isinstance(params, dict):
                data = urllib.urlencode(params)
            else:
                data = params
        if data is not None:
            return  self.opener.open(urljoin(self.base_url, path), data)
        return self.opener.open(urljoin(self.base_url, path))

    def create_invoice(self, invoice_number, total_gross):
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
            invoice.save()

        return invoice

    def save_document(self, invoice, data, title="Faktura"):
        document = models.Document()
        document.invoice = invoice
        document.title = title
        document.document_file.save('%s.pdf' % uuid.uuid4(), ContentFile(data.read()), save=True)
        document.save()
        logger.info("Downloaded file for invoice %s: %s (size: %s)", invoice.number, document.document_file.name, document.document_file.size)
