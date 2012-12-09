#!/usr/bin/python
# -*- coding: utf8 -*-

from django.conf import settings
import re
from BaseScrapper import BaseScrapper
from lxml import etree
import logging

logger = logging.getLogger(__name__)


class PlusGSMScrapper(BaseScrapper):

    company_name = "Plus GSM"
    base_url = "https://ssl.plusgsm.pl"

    def __init__(self):
        super(PlusGSMScrapper, self).__init__()

    def download_invoices(self, configuration):
        self.get('/ebok-web/basic/loginStep1.action')
        ret = self.get(
            '/ebok-web/basic/loginStep2.action',
            params={'msisdn': configuration['username'],
                    'password': configuration['password']}
        )

        if "wystąpił błąd aplikacji" in ret.read():
            logger.error("I can't sign in :(")
            return

        parser = etree.HTMLParser()
        tree = etree.parse(
            self.get('/ebok-web/spectrum/payments/showPaymentsHistory.action',
                     referer='/ebok-web/spectrum/welcome.action'),
            parser
        )

        for tr in tree.xpath("//form[@id='payForm']//tbody/tr"):

            td2 = tr.xpath('./td[2]/strong')
            td7 = tr.xpath("./td[7]/a[contains(@onclick, 'openWindow')][1]")

            if len(td2) < 1 or len(td7) < 1:
                continue

            if td2[0].text.strip() == "Faktura" and td7[0].text.strip() == "Faktura":
                # kolumna "Numer faktury"
                td5 = tr.xpath('./td[5]/strong')
                # kolumna "Kwota (z VAT)"
                td6 = tr.xpath('./td[6]/strong')
                # kolumna "Dokumenty pdf"
                td7 = tr.xpath(
                    "./td[7]/a[contains(@onclick, 'openWindow')]/@onclick")

                position_on_list = td7[0].split("'")[1].split("=")[1]
                invoice_id = td5[0].text.strip()
                total_gross = re.sub(
                    "[^0-9,]", "", td6[0].text.strip()).replace(',', '.')

                invoice = self.create_invoice(invoice_id, total_gross)

                if invoice:
                    # faktura
                    self.get('/ebok-web/spectrum/payments/downloadInvoice.action?positionOnList=' + str(position_on_list))
                    self.save_document(invoice, self.get('/ebok-web/spectrum/brpDocumentDownload/downloadDocument.action'))
                    # rachunek szczegolowy
                    self.get('/ebok-web/spectrum/payments/downloadInvoiceDetails.action?positionOnList=' + str(position_on_list))
                    self.save_document(invoice, self.get('/ebok-web/spectrum/brpDocumentDownload/downloadDocument.action'), title="Rachunek szczegółowy")
