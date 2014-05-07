# -*- coding: utf-8 -*-

import unittest2 as unittest

from datetime import datetime, timedelta

from zope.component import getUtility, getMultiAdapter

from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import logout

from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.interfaces import IPortletTypeInterface

from s17.portlets import birthdayportlet
from s17.portlets.testing import INTEGRATION_TESTING


class BirthdayPortletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.name = 's17.portlets.birthday.BirthdayPortlet'
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


class BirthdayRendererTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.pw = getToolByName(self.portal, 'portal_workflow')
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.pw.setChainForPortalTypes(['Person'],
                                       ['simple_publication_workflow'])

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
        # first let's create some persons and set their birthdays
        birthday = datetime.date(datetime.now())
        names = ['Juan Perez', 'Gustavo Roner', 'Marcelo Santos',
                 'Marcelo Alves', 'Julia Alvarez']
        for i, name in enumerate(names):
            self.portal.invokeFactory('Person',
                                      name,
                                      given_name=name.split()[0],
                                      surname=name.split()[1],
                                      birthday=birthday + timedelta(days=i / 2))

        # since they weren't published, portlet shouldn't listed them
        render = self.renderer(
            context=self.portal,
            assignment=birthdayportlet.Assignment('test', 30)
        )
        mapping = render.get_birthdays()
        mapping = [[person[0] for person in person] for person in
                   mapping.values()]
        self.assertEquals([], mapping)

        # let's publish the items
        for name in names:
            self.pw.doActionFor(self.portal[name], 'publish')

        # and test if names are listed in the right order and grouping
        mapping = render.get_birthdays()
        mapping = [[person[0] for person in person] for person in
                   mapping.values()]
        self.assertEquals([['Gustavo Roner', 'Juan Perez'],
                           ['Marcelo Alves', 'Marcelo Santos'],
                           ['Julia Alvarez']],
                          mapping)

    def test_is_anonymous(self):
        render = self.renderer(context=self.portal,
                               assignment=birthdayportlet.Assignment('test', 5))
        self.assertFalse(render.is_anonymous)
        logout()
        self.assertTrue(render.is_anonymous)

    def test_available(self):
        # we should not see this portlet if there are no birthdays to display
        render = self.renderer(context=self.portal,
                               assignment=birthdayportlet.Assignment('test', 5))
        self.assertFalse(render.available)

        # but if we create and publish some Person items
        birthday1 = datetime.date(datetime.now())
        birthday2 = datetime.date(datetime.now() + timedelta(days=3))
        self.portal.invokeFactory('Person',
                                  TEST_USER_ID, birthday=birthday1)
        self.portal.invokeFactory('Person',
                                  'name2', birthday=birthday2)
        self.pw.doActionFor(self.portal[TEST_USER_ID], 'publish')
        self.pw.doActionFor(self.portal['name2'], 'publish')

        # we should be able to see it
        render = self.renderer(context=self.portal,
                               assignment=birthdayportlet.Assignment('test', 5))
        self.assertTrue(render.available)

        # except if we are anonymous
        logout()
        self.assertFalse(render.available)

    def test_long_period(self):
        render = self.renderer(context=self.portal,
                               assignment=birthdayportlet.Assignment('test', 365))
        self.assertFalse(render.available)
        birthday1 = datetime.date(datetime.now())
        birthday2 = datetime.date(datetime.now() + timedelta(days=364))
        self.portal.invokeFactory('Person',
                                  'name1', birthday=birthday1)
        self.portal.invokeFactory('Person',
                                  'name2', birthday=birthday2)
        self.pw.doActionFor(self.portal['name1'], 'publish')
        self.pw.doActionFor(self.portal['name2'], 'publish')
        mapping = render.get_birthdays()
        self.assertEquals(2, len(mapping))
