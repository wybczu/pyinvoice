#!/usr/bin/python
# -*- coding: utf8 -*-

import logging
import time
import re

from bs4 import BeautifulSoup
from BaseScrapper import BaseScrapper

logger = logging.getLogger(__name__)


class UPCScrapper(BaseScrapper):

    company_name = "UPC"
    base_url = "https://ebok.upc.pl"

    def __init__(self):
        super(UPCScrapper, self).__init__()

    def download_invoices(self, configuration):

        res = self.get('/')

        soup = BeautifulSoup(res.content, from_encoding=res.encoding)

        login_url = soup.form['action'].replace(self.base_url, '')

        res = self.get(
            login_url,
            params={
                '_58a_login': configuration['username'],
                '_58a_password': configuration['password'],
                '_58a_redirect': ''
            }
        )

        if not res.url == self._url('ebok'):
            logger.error("I can't sign in :(")
            return

        self.get('/lista-efaktur')

        params = {
            '_search': 'false',
            'nd': int(time.time() * 1000.0),
            'rows': 10,
            'page': '1',
            'sidx': 'id',
            'sord': 'desc',
        }

        res = self.get('/en/grid/invoices', params=params)

        invoices_soup = BeautifulSoup(res.content, from_encoding=res.encoding)

        for row in invoices_soup.find_all('row'):
            invoice_id = row.id.text
            invoice_number = row.number.text
            total_gross = re.sub("[^0-9,]", "", row.amount.text).replace(',', '.')
            invoice = self.create_invoice(invoice_number, total_gross)

            if invoice:
                res = self.get('/pl/operations', params={'action': 'pdf', 'invoiceId': invoice_id})
                self.save_document(invoice, res)
