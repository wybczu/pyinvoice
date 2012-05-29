#!/usr/bin/python
# -*- coding: utf8 -*-

from lxml import etree
import cookielib, urllib2, urllib
import time, random
from urlparse import urljoin
import os.path
import logging
from BaseScrapper import BaseScrapper
import re
import logging

logger = logging.getLogger(__name__)

UPC_XMLNS = {
    'soap' : 'http://schemas.xmlsoap.org/soap/envelope',
    'ns4'  : "http://domain.ebok.upc.com/jaws",
    'ns3'  : "http://services.ebok.upc.com/jaws",
    'ns2'  : "http://ebok.service",
}

UPC_SOAP_INVOICES_TPL = """
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <SOAP-ENV:Body>
        <tns:getClientInvoices xmlns:tns="http://ebok.service">
            <tns:String_1>%s</tns:String_1>
        </tns:getClientInvoices>
    </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""

class UPCScrapper(BaseScrapper):

    company_name = "UPC"
    base_url = "https://ebok.upc.pl"

    def __init__(self):
        super(UPCScrapper, self).__init__()

    def download_invoices(self, configuration):

        parser = etree.HTMLParser()
        self.get('/')
        tree = etree.parse(self.get('/'), parser)
        
        # form action
        login_form = tree.xpath("//form")[0]
        login_url = login_form.attrib["action"].replace(self.base_url, '')

        ret = self.get(
            login_url, 
            params={
                '_58_login' : configuration['username'], 
                '_58_password' : configuration['password'], 
                '_58_redirect' : ''
            }
        )        

        match = re.search(r"sessionID=([a-z0-9]*).*", ret.read())
        if match:
            session_id = match.group(1)

        # soap request
        tree = etree.parse(
            self.get(
                '/upc-eBok-invoice-0/WSFlexServiceBean',
                params = UPC_SOAP_INVOICES_TPL % session_id, 
                headers = [('Content-Type', 'text/xml; charset=utf-8'), ('SOAPAction', '""')]
            )
        )                

        for element in tree.xpath("//ns2:ClientInvoices", namespaces=UPC_XMLNS):
            
            invoice_id = element.xpath("./ns4:invoiceId", namespaces=UPC_XMLNS)[0].text 
            invoice_number = element.xpath("./ns4:invoiceNumber", namespaces=UPC_XMLNS)[0].text
            total_gross = element.xpath("./ns4:totalGross", namespaces=UPC_XMLNS)[0].text

            invoice = self.create_invoice(invoice_number, total_gross)

            if invoice:
                self.save_document(
                    invoice,
                    self.get('/console/pdf?%s' % urllib.urlencode({'sessionId': session_id, 'invoiceId': invoice_id}))
                )


