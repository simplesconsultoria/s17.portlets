# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import getUtility, getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import _getDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.interfaces import IPortletTypeInterface

from s17.portlets import whitepagesportlet

from s17.portlets.testing import INTEGRATION_TESTING


class WhitePagesPortletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.name = 's17.portlets.whitepages.WhitePagesPortlet'
        self.pw = getToolByName(self.portal, 'portal_workflow')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.pw.setChainForPortalTypes(['Person'],
                                       ['simple_publication_workflow'])

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

    def test_whitepages_view(self):
        index = 0
        while index < 4:
            self.portal.invokeFactory('Person',
                                      'person%s' % index,
                                      given_name='Person %s' % index,
                                      surname='surname%s' % index)
            self.pw.doActionFor(self.portal['person%s' % index], 'publish')
            index += 1

        self.request.form = {'fullname': 'Person'}
        view = self.portal.unrestrictedTraverse('@@whitepages')
        people = view.people_list()
        self.assertEqual(4, len(people))


class WhitePagesRendererTestCase(unittest.TestCase):

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
        self.assertNotEqual(None, html)
        self.assertNotEqual('', html)
