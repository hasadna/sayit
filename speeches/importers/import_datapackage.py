# -*- coding: utf-8 -*-

import logging
import datapackage

from speeches.importers.import_base import ImporterBase
from speeches.models import Section, Speech, Speaker


logger = logging.getLogger(__name__)


class ImportDatapackage(ImporterBase):

    def import_document(self, document_path):
        dp = datapackage.DataPackage(document_path)
