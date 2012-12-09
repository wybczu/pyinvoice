#!/usr/bin/python
# -*- coding: utf8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import logging


class Command(BaseCommand):
    help = 'Downloads invoices'

    def _get_scrapper(self, name):
        m = __import__(name)
        for n in name.split(".")[1:]:
            m = getattr(m, n)
        m = getattr(m, n)
        return m

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        for scrapper in settings.INVOICE_SCRAPPERS:
            logger.info("Firing %s", scrapper)
            scrapper_obj = self._get_scrapper(scrapper)()
            scrapper_obj.download_invoices(
                settings.INVOICE_SCRAPPERS_CONFIGURATION[scrapper])
