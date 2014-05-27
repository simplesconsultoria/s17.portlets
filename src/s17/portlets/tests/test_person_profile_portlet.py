# -*- coding: utf-8 -*-
from plone import api
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from Products.GenericSetup.utils import _getDottedName
from s17.portlets import personprofile
from s17.portlets.testing import INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class PersonProfilePortletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.name = 's17.portlets.personprofile.PersonProfile'
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name=self.name)
        self.assertEqual(portlet.addview, self.name)

    def test_registered_interfaces(self):
        portlet = getUtility(IPortletType, name=self.name)
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        expected = [
            'plone.app.portlets.interfaces.IColumn',
            'plone.app.portlets.interfaces.IDashboard'
        ]
        self.assertEqual(registered_interfaces, expected)

    def test_interfaces(self):
        portlet = personprofile.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType, name=self.name)
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(
            isinstance(mapping.values()[0], personprofile.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.request

        mapping['foo'] = personprofile.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.assertTrue(isinstance(editview, personprofile.EditForm))

    def test_renderer(self):
        context = self.portal
        request = self.request
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(
            IPortletManager, name='plone.leftcolumn', context=self.portal)

        assignment = personprofile.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.assertTrue(isinstance(renderer, personprofile.Renderer))


class PersonProfileRendererTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # setRoles(self.portal, TEST_USER_ID, ['Member'])

    def renderer(
            self,
            context=None,
            request=None,
            view=None,
            manager=None,
            assignment=None
    ):
        context = context or self.portal
        request = request or self.request
        view = view or context.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.leftcolumn', context=self.portal)

        assignment = assignment or personprofile.Assignment()
        return getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)

    def test_available(self):
        r = self.renderer()
        self.assertTrue(r.available)
        logout()
        self.assertFalse(r.available)

    def test_show_title(self):
        r = self.renderer()
        self.assertTrue(r.show_title)
        self.assertIn(u'User Profile', r.render())

        r = self.renderer(
            assignment=personprofile.Assignment(show_title=False))
        self.assertFalse(r.show_title)
        self.assertNotIn(u'User Profile', r.render())

    def test_show_edit_profile_link(self):
        r = self.renderer()
        self.assertTrue(r.show_edit_profile_link)
        self.assertIn(u'Edit profile', r.render())

        r = self.renderer(
            assignment=personprofile.Assignment(show_edit_profile_link=False))
        self.assertFalse(r.show_edit_profile_link)
        self.assertNotIn(u'Edit profile', r.render())

    def test_show_logout_link(self):
        r = self.renderer()
        self.assertTrue(r.show_logout_link)
        self.assertIn(u'Log out', r.render())

        r = self.renderer(
            assignment=personprofile.Assignment(show_logout_link=False))
        self.assertFalse(r.show_logout_link)
        self.assertNotIn(u'Log out', r.render())

    def test_show_recent_content(self):
        latest_content_msg = u'Latest content created by you:'
        all_content_msg = u'All content created by you'
        search_url = u'http://nohost/plone/search?Creator=test_user_1_&amp;sort_on=created&amp;sort_order=reverse'
        r = self.renderer()
        self.assertTrue(r.show_recent_content)
        self.assertNotIn(latest_content_msg, r.render())
        self.assertNotIn(all_content_msg, r.render())
        self.assertNotIn(search_url, r.render())

        with api.env.adopt_roles(['Manager']):
            api.content.create(self.portal, 'Document', title='Lorem ipsum')

        r = self.renderer()
        self.assertTrue(r.show_recent_content)
        self.assertIn(latest_content_msg, r.render())
        self.assertIn(all_content_msg, r.render())
        self.assertIn(search_url, r.render())

        r = self.renderer(
            assignment=personprofile.Assignment(show_recent_content=False))
        self.assertFalse(r.show_recent_content)
        self.assertNotIn(latest_content_msg, r.render())
        self.assertNotIn(all_content_msg, r.render())
        self.assertNotIn(search_url, r.render())

    def test_get_user_content(self):
        r = self.renderer()
        self.assertEqual(r.get_user_content(), [])

        with api.env.adopt_roles(['Manager']):
            api.content.create(self.portal, 'Document', title='Lorem ipsum')

        r = self.renderer()
        content = r.get_user_content()
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0].Title, 'Lorem ipsum')
        self.assertEqual(content[0].portal_type, 'Document')

    def test_user_has_content(self):
        r = self.renderer()
        self.assertFalse(r.user_has_content)

        with api.env.adopt_roles(['Manager']):
            api.content.create(self.portal, 'Document', title='Lorem ipsum')

        r = self.renderer()
        self.assertTrue(r.user_has_content)
