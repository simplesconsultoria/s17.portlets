# -*- coding: utf-8 -*-
from os import path
from plone import api
from plone.app.testing import TEST_USER_ID
# from plone.namedfile.file import NamedBlobImage
from s17.portlets.config import HAS_PERSON
from s17.portlets.testing import INTEGRATION_TESTING
from s17.portlets.utils import get_portrait_url
from s17.portlets.utils import sort_birthdays

import unittest

abspath = path.abspath(path.dirname(__file__))
data = open(path.join(abspath, 'person.png')).read()


class UtilsTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_get_portrait_url_for_user(self):
        self.assertEqual(
            get_portrait_url(TEST_USER_ID),
            'http://nohost/plone/defaultUser.png',
        )

    @unittest.skipUnless(HAS_PERSON, 'test depends on s17.person')
    def test_get_portrait_url_for_person(self):
        with api.env.adopt_roles(['Manager']):
            person = api.content.create(self.portal, 'Person', 'person')

        self.assertEqual(
            get_portrait_url(person),
            'http://nohost/plone/defaultUser.png',
        )

        # FIXME: ComponentLookupError: (<InterfaceClass plone.namedfile.interfaces.IStorage>, '__builtin__.str')
        # person.picture = NamedBlobImage(data, 'image/png', 'person.png')

        # self.assertEqual(
        #     get_portrait_url(person),
        #     'http://nohost/plone/defaultUser.png',
        # )

    def test_sort_birthdays(self):
        birthdays = [
            dict(birthday='19/07', fullname='FFF'),
            dict(birthday='19/07', fullname='EEE'),
            dict(birthday='01/01', fullname='DDD'),
            dict(birthday='28/01', fullname='CCC'),
            dict(birthday='01/01', fullname='BBB'),
            dict(birthday='28/01', fullname='AAA'),
        ]
        sorted_birthdays = sort_birthdays(birthdays)
        days = [day for day in sorted_birthdays]
        # we have 3 different dates: 01/01, 28/01 and 19/07
        self.assertEqual(len(days), 3)
        # we test each date do see if it is sorted
        self.assertEqual(
            sorted_birthdays[days[0]],
            [
                {'fullname': 'BBB', 'birthday': '01/01'},
                {'fullname': 'DDD', 'birthday': '01/01'}
            ]
        )
        self.assertEqual(
            sorted_birthdays[days[1]],
            [
                {'fullname': 'AAA', 'birthday': '28/01'},
                {'fullname': 'CCC', 'birthday': '28/01'},
            ]
        )
        self.assertEqual(
            sorted_birthdays[days[2]],
            [
                {'fullname': 'EEE', 'birthday': '19/07'},
                {'fullname': 'FFF', 'birthday': '19/07'},
            ]
        )
