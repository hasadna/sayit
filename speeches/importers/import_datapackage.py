# -*- coding: utf-8 -*-

import logging
from datetime import datetime

import datapackage
import speeches
from django.db import transaction

from speeches.importers.import_base import ImporterBase
from speeches.models import Section, Speech, Speaker

logger = logging.getLogger(__name__)


class ImportDatapackage(ImporterBase):
    def import_document(self, document_path):
        dp = datapackage.DataPackage(document_path)
        return dp

    @transaction.atomic
    def get_persons_data(self, dp):
        persons = next((resource for resource in dp.resources if resource.descriptor['name'] == 'persons-person'),
                       None)
        # One day this information will be useful, but not now...
        # positions = next((resource for resource in dp.resources if resource.descriptor['name'] == 'persons-position'),
        #                  None)
        # persons_to_positions = next(
        #     (resource for resource in dp.resources if resource.descriptor['name'] == 'persons-persons-to-positions'),
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

    def get_committee_data(self, dp):
        # TODO: Optimization for imports: the object id from the data is saved as 'session'
        # and then a search for parents is done by session in order to retrieve the id in the Section model

        committees = next((resource for resource in dp.resources if resource.descriptor['name'] == 'committees'),
                          None)

        meetings = next((resource for resource in dp.resources if resource.descriptor['name'] == 'committee-meetings'),
                        None)

        if committees is not None:
            with transaction.atomic():
                for committee in committees.data:
                    section = Section(instance=self.instance)
                    section.session = committee['id']
                    section.heading = committee['name']
                    section.description = committee['description']
                    if committee['parent_id']:
                        parent = Section.objects.filter(session=committee['parent_id']).first()
                        if parent:
                            section.parent_id = parent.id
                    section.save()

        if meetings is not None:
            with transaction.atomic():
                for meeting in meetings.data:
                    section = Section(instance=self.instance)
                    section.heading = meeting['title']
                    if meeting['committee_id']:
                        parent = Section.objects.filter(session=meeting['committee_id']).first()
                        if parent:
                            section.parent_id = parent.id
                    start_datetime = datetime.strptime(meeting['start_datetime '], '%Y-%m-%dT%H:%M:%S')
                    section.start_date = start_datetime.date()
                    section.start_time = start_datetime.time()
                    section.session = meeting['id']
                    section.save()
