# -*- coding: utf-8 -*-
from datetime import datetime
from plone import api
from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.namedfile import NamedImage
from plone.namedfile.tests.base import getFile
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from s17.portlets import personprofile
from s17.portlets.config import HAS_PERSON
from s17.portlets.testing import INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.component import getUtility

import os
import unittest


class PersonProfilePortletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        if not HAS_PERSON:
            self.skipTest('test depends on s17.person')

        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.name = 's17.portlets.personprofile.PersonProfile'
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name=self.name)
        self.assertEqual(portlet.addview, self.name)

    def test_registered_type_interfaces(self):
        iface = getUtility(IPortletTypeInterface, name=self.name)
        self.assertEqual(personprofile.IPersonProfile, iface)

    def test_interfaces(self):
        portlet = personprofile.Assignment('test')
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType, name=self.name)
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'portlet_title': 'test'})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(
            isinstance(mapping.values()[0], personprofile.Assignment))

    def test_invoke_edit_view(self):
        # NOTE: This test can be removed if the portlet has no edit form
        mapping = PortletAssignmentMapping()
        request = self.request

        mapping['foo'] = personprofile.Assignment('test')
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.assertTrue(isinstance(editview, personprofile.EditForm))

    def test_obtain_renderer(self):
        context = self.portal
        request = self.request
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        assignment = personprofile.Assignment('test')

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.assertTrue(isinstance(renderer, personprofile.Renderer))


class PersonProfileRendererTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        if not HAS_PERSON:
            self.skipTest('test depends on s17.person')

        self.portal = self.layer['portal']
        self.pw = api.portal.get_tool('portal_workflow')
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('News Item', 'news1')
        image = os.path.join(os.path.dirname(__file__), 'picture.jpg')
        data = getFile(image).read()
        self.portal.invokeFactory(
            'Person',
            TEST_USER_ID,
            birthday=datetime.date(datetime.now()),
            picture=NamedImage(data)
        )
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.render = self.renderer(
            context=self.portal, assignment=personprofile.Assignment('test'))

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.portal
        request = request or self.request
        view = view or context.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = assignment or personprofile.Assignment('test')
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def test_get_user_id(self):
        self.assertEqual(TEST_USER_ID, self.render.get_user_id())

    def test_get_user_profile(self):
        suppose_url = self.portal.absolute_url() + '/' + TEST_USER_ID
        self.assertEqual(suppose_url, self.render.get_user_profile())

    def test_get_person(self):
        user = self.render.get_person(TEST_USER_ID)
        self.assertEqual(self.portal[TEST_USER_ID], user.getObject())

    def test_get_participation(self):
        """ Participation in creation of 6 content types: Five News Item
            and a s17.person.person. Returns at most five.
        """
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        index = 2
        while index < 6:
            self.portal.invokeFactory('News Item', 'news%s' % index)
            index += 1
        user = self.render.get_participation()
        self.assertEqual(5, len(user))
        self.assertEqual(self.portal[TEST_USER_ID], user[4].getObject())

    def get_sizes_from_str(self, string):
        sizes = string[string.find('height'):].split(' ')
        height = sizes[0].strip('height="')
        width = sizes[1].strip('width="')
        return (height, width)

    def test_get_portrait(self):
        size = ('250', '200')
        self.assertEqual(
            size, self.get_sizes_from_str(self.render.get_portrait()))

    def test_data_transform(self):
        date = datetime.now()
        day, month, year = date.day, date.month, date.year
        output = '%s/%s/%s' % \
            (str(day).zfill(2), str(month).zfill(2), str(year).zfill(2))
        self.assertEqual(output, self.render.data_transform(date))
