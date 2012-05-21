# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import unittest2 as unittest

import os

from zope.component import getUtility, getMultiAdapter

from Products.GenericSetup.utils import _getDottedName

from plone.namedfile import NamedImage
from plone.namedfile.tests.base import getFile

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import setRoles
from plone.app.testing import login

from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.interfaces import IPortletTypeInterface

from s17.person.portlets import birthdayportlet
from s17.person.portlets import personprofile
from s17.person.portlets import whitepagesportlet

from s17.person.portlets.testing import INTEGRATION_TESTING


class TestBirthdayPortlet(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.name = 's17.person.portlets.birthday.BirthdayPortlet'
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name=self.name)
        self.assertEquals(portlet.addview, self.name)

    def test_registered_type_interfaces(self):
        iface = getUtility(IPortletTypeInterface, name=self.name)
        self.assertEquals(birthdayportlet.IBirthdayPortlet, iface)

    def test_interfaces(self):
        portlet = birthdayportlet.Assignment('test', 5)
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType, name=self.name)
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'portlet_title': 'test', 'days_number': 5})

        self.assertEquals(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0],
                                   birthdayportlet.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.request

        mapping['foo'] = birthdayportlet.Assignment('test', 5)
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, birthdayportlet.EditForm))

    def test_obtain_renderer(self):
        context = self.portal
        request = self.request
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        assignment = birthdayportlet.Assignment('test', 5)

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.assertTrue(isinstance(renderer, birthdayportlet.Renderer))


class TestBirthdayRenderer(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.portal_workflow.setChainForPortalTypes(
            ['collective.person.person'], ['simple_publication_workflow'])

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.portal
        request = request or self.request
        view = view or context.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = assignment or birthdayportlet.Assignment('test', 5)
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def test_get_birthdays(self):
        birthday1 = datetime.date(datetime.now())
        birthday2 = datetime.date(datetime.now() + timedelta(days=3))
        self.portal.invokeFactory('collective.person.person',
                                  TEST_USER_ID, birthday=birthday1)
        self.portal.invokeFactory('collective.person.person',
                                  'name2', birthday=birthday2)
        self.portal.portal_workflow.doActionFor(
                                    self.portal[TEST_USER_ID], 'publish')
        self.portal.portal_workflow.doActionFor(self.portal.name2, 'publish')
        render = self.renderer(context=self.portal,
                          assignment=birthdayportlet.Assignment('test', 5))
        items = render.get_birthdays()
        self.assertEquals(2, len(items))


class TestPersonProfilePortlet(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.name = 's17.person.portlets.personprofile.PersonProfile'
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name=self.name)
        self.assertEquals(portlet.addview, self.name)

    def test_registered_type_interfaces(self):
        iface = getUtility(IPortletTypeInterface, name=self.name)
        self.assertEquals(personprofile.IPersonProfile, iface)

    def test_interfaces(self):
        portlet = personprofile.Assignment('test')
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType, name=self.name)
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'portlet_title': 'test'})

        self.assertEquals(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0],
                                personprofile.Assignment))

    def test_invoke_edit_view(self):
        # NOTE: This test can be removed if the portlet has no edit form
        mapping = PortletAssignmentMapping()
        request = self.request

        mapping['foo'] = personprofile.Assignment('test')
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, personprofile.EditForm))

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


class TestPersonProfileRenderer(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.portal_workflow.setChainForPortalTypes(
            ['collective.person.person'], ['simple_publication_workflow'])
        self.portal.invokeFactory('News Item', 'news1')
        image = os.path.join(os.path.dirname(__file__), 'picture.jpg')
        data = getFile(image).read()
        self.portal.invokeFactory('collective.person.person', TEST_USER_ID,
            birthday=datetime.date(datetime.now()),
            picture=NamedImage(data))
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.render = self.renderer(context=self.portal,
                          assignment=personprofile.Assignment('test'))

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
        self.assertEquals(TEST_USER_ID, self.render.get_user_id())

    def test_get_user_profile(self):
        suppose_url = self.portal.absolute_url() + '/' + TEST_USER_ID
        self.assertEquals(suppose_url, self.render.get_user_profile())

    def test_get_person(self):
        user = self.render.get_person(TEST_USER_ID)
        self.assertEquals(self.portal[TEST_USER_ID], user.getObject())

    def test_get_participation(self):
        user = self.render.get_participation()
        self.assertEquals(1, len(user))
        self.assertEquals(self.portal[TEST_USER_ID], user[0].getObject())

    def get_sizes_from_str(self, string):
        sizes = string[string.find('height'):].split(' ')
        height = sizes[0].strip('height="')
        width = sizes[1].strip('width="')
        return (height, width)

    def test_get_portrait(self):
        size = ('250', '200')
        self.assertEquals(size,
            self.get_sizes_from_str(self.render.get_portrait()))

    def test_data_transform(self):
        date = datetime.now()
        day, month, year = date.day, date.month, date.year
        output = '%s/%s/%s' % \
            (str(day).zfill(2), str(month).zfill(2), str(year).zfill(2))
        self.assertEquals(output, self.render.data_transform(date))


class TestWhitePagesPortlet(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.name = 's17.person.portlets.whitepages.WhitePagesPortlet'
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name=self.name)
        self.assertEquals(portlet.addview, self.name)

    def test_registered_type_interfaces(self):
        iface = getUtility(IPortletTypeInterface, name=self.name)
        self.assertEquals(whitepagesportlet.IWhitePagesPortlet, iface)

    def test_registered_interfaces(self):
        portlet = getUtility(IPortletType, name=self.name)
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual(
            ['plone.app.portlets.interfaces.IColumn',
             'plone.app.portlets.interfaces.IDashboard'],
            registered_interfaces)

    def test_interfaces(self):
        portlet = whitepagesportlet.Assignment('test')
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType, name=self.name)
        mapping = self.portal.restrictedTraverse(
                        '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'portlet_title': 'test'})

        self.assertEquals(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0],
                        whitepagesportlet.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.request

        mapping['foo'] = whitepagesportlet.Assignment('test')
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, whitepagesportlet.EditForm))

    def test_obtain_renderer(self):
        context = self.portal
        request = self.request
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        assignment = whitepagesportlet.Assignment('test')

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.assertTrue(isinstance(renderer, whitepagesportlet.Renderer))


class TestWhitePagesRenderer(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.portal
        request = request or self.request
        view = view or context.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager,
                    name='plone.rightcolumn', context=self.portal)

        assignment = assignment or whitepagesportlet.Assignment('tests')
        return getMultiAdapter((context, request, view, manager, assignment),
                                IPortletRenderer)

    def test_render(self):
        render = self.renderer(context=self.portal,
                          assignment=whitepagesportlet.Assignment('test'))
        html = render.render()
        self.assertNotEquals(None, html)
        self.assertNotEquals('', html)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
