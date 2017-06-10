# -*- coding: utf-8 -*-

import logging
import datapackage

from speeches.importers.import_base import ImporterBase
from speeches.models import Section, Speech, Speaker

logger = logging.getLogger(__name__)


class ImportDatapackage(ImporterBase):
    def import_document(self, document_path):
        dp = datapackage.DataPackage(document_path)
        return dp

    def get_persons_data(self, dp):
        persons = next((resource for resource in dp.resources if resource.descriptor['name'] == u'persons-person'),
                       None)
        # One day this information will be useful, but not now...
        # positions = next((resource for resource in dp.resources if resource.descriptor['name'] == u'persons-position'),
        #                  None)
        # persons_to_positions = next(
        #     (resource for resource in dp.resources if resource.descriptor['name'] == u'persons-persons-to-positions'),
        #     None)
        if persons is not None:
            for person in persons.data:
                speaker = Speaker(instance=self.instance)
                speaker.given_name = person['first_name']
                speaker.family_name = person['last_name']
                speaker.name = speaker.given_name + ' ' + speaker.family_name
                speaker.email = person['email']
                speaker.gender = person['gender_description']
                speaker.save()
