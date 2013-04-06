#!/usr/bin/python
# -*- coding: utf8 -*-

import re
import logging

from bs4 import BeautifulSoup
from BaseScrapper import BaseScrapper

logger = logging.getLogger(__name__)


class PlusGSMScrapper(BaseScrapper):

    company_name = "Plus GSM"
    base_url = "https://ssl.plusgsm.pl"

    def __init(self):
        super(PlusGSMScrapper, self).__init__()

    def download_invoices(self, configuration):

        self.get('/ebok-web/basic/loginStep1.action')

        payload = {
            'msisdn': configuration['username'],
            'password': configuration['password'],
        }

        r = self.post('/ebok-web/basic/loginStep2.action', payload)

        if u'wystąpił błąd aplikacji' in r.content:
            logger.error("I can't sign in :(")
            return

        r = self.get('/ebok-web/spectrum/payments/showPaymentsHistory.action')

        soup = BeautifulSoup(r.content, from_encoding=r.encoding)
        invoices_soup = soup.find("form", id="payForm")

        for row in invoices_soup.find_all("tr"):
            if not row.find("input"):
                continue
            columns = row.find_all("td")
            # jako invoice_id używam numeru faktury
            _, _, date, _, invoice_id, total_gross, _ = [x.text.strip() for x in columns]
            (position_on_list,) = re.search(r'positionOnList=(\d)', columns[6].a['onclick']).groups()  # pozycja faktury na liście
            total_gross = re.sub("[^0-9,]", "", total_gross).replace(',', '.')  # Kwota (z VAT)

            invoice = self.create_invoice(invoice_id, total_gross, date)

            if invoice:
                # faktura
                self.get('/ebok-web/spectrum/payments/downloadInvoice.action?positionOnList=' + str(position_on_list))
                self.save_document(invoice, self.get('/ebok-web/spectrum/brpDocumentDownload/downloadDocument.action'))
                # rachunek szczegolowy
                self.get('/ebok-web/spectrum/payments/downloadInvoiceDetails.action?positionOnList=' + str(position_on_list))
                self.save_document(invoice, self.get('/ebok-web/spectrum/brpDocumentDownload/downloadDocument.action'), title="Rachunek szczegółowy")
