# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from plone import api
from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from s17.portlets import birthdayportlet
from s17.portlets.config import HAS_PERSON
from s17.portlets.testing import INTEGRATION_TESTING
from s17.portlets.utils import sort_birthdays
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class BirthdayPortletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.name = 's17.portlets.birthday.BirthdayPortlet'
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name=self.name)
        self.assertEqual(portlet.addview, self.name)

    def test_registered_type_interfaces(self):
        iface = getUtility(IPortletTypeInterface, name=self.name)
        self.assertEqual(birthdayportlet.IBirthdayPortlet, iface)

    def test_interfaces(self):
        portlet = birthdayportlet.Assignment(5)
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType, name=self.name)
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'days_number': 5})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(
            isinstance(mapping.values()[0], birthdayportlet.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.request

        mapping['foo'] = birthdayportlet.Assignment(5)
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.assertTrue(isinstance(editview, birthdayportlet.EditForm))

    def test_obtain_renderer(self):
        context = self.portal
        request = self.request
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = birthdayportlet.Assignment(5)

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.assertTrue(isinstance(renderer, birthdayportlet.Renderer))


# TODO: split in two test cases: one for person and one for user
class BirthdayRendererTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.pw = api.portal.get_tool('portal_workflow')
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

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
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = assignment or birthdayportlet.Assignment(5)
        return getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)

    @unittest.skipUnless(HAS_PERSON, 'test depends on s17.person')
    def test_data(self):
        # first let's create some persons and set their birthdays
        birthday = datetime.date(datetime.now())
        names = [
            'Juan Perez',
            'Gustavo Roner',
            'Marcelo Santos',
            'Marcelo Alves',
            'Julia Alvarez',
        ]
        for i, name in enumerate(names):
            self.portal.invokeFactory(
                'Person',
                name,
                given_name=name.split()[0],
                surname=name.split()[1],
                birthday=birthday + timedelta(days=i / 2)
            )

        # since they weren't published, portlet shouldn't listed them
        render = self.renderer(assignment=birthdayportlet.Assignment(30))
        birthdays = render._data()
        self.assertEqual(len(birthdays), 0)

        # let's publish the items
        for name in names:
            self.pw.doActionFor(self.portal[name], 'publish')

        # and test if names are listed in the right order and grouping
        render = self.renderer(assignment=birthdayportlet.Assignment(30))
        birthdays = render._data()
        expected = [
            ['Gustavo Roner', 'Juan Perez'],
            ['Marcelo Alves', 'Marcelo Santos'],
            ['Julia Alvarez'],
        ]
        for i, day in enumerate(birthdays):
            names = [info['fullname'] for info in birthdays[day]]
            self.assertEqual(names, expected[i])

    # FIXME: we need to test this for users
    @unittest.skipUnless(HAS_PERSON, 'test depends on s17.person')
    def test_available(self):
        # we should not see this portlet if there are no birthdays to display
        render = self.renderer(assignment=birthdayportlet.Assignment(5))
        self.assertFalse(render.available)

        # let's create and publish a Person
        birthday = datetime.date(datetime.now())
        self.portal.invokeFactory('Person', 'person', birthday=birthday)
        self.pw.doActionFor(self.portal['person'], 'publish')

        # we should be able to see it
        render = self.renderer(assignment=birthdayportlet.Assignment(5))
        self.assertTrue(render.available)

        # except if we are anonymous
        logout()
        self.assertFalse(render.available)

    @unittest.skipUnless(HAS_PERSON, 'test depends on s17.person')
    def test_long_period(self):
        render = self.renderer(assignment=birthdayportlet.Assignment(365))
        self.assertFalse(render.available)
        birthday1 = datetime.date(datetime.now())
        birthday2 = datetime.date(datetime.now() + timedelta(days=364))
        self.portal.invokeFactory('Person', 'name1', birthday=birthday1)
        self.portal.invokeFactory('Person', 'name2', birthday=birthday2)
        self.pw.doActionFor(self.portal['name1'], 'publish')
        self.pw.doActionFor(self.portal['name2'], 'publish')
        birthdays = render.get_birthdays_from_persons()
        birthdays = sort_birthdays(birthdays)
        self.assertEqual(2, len(birthdays))

    def test_in_range(self):
        render = self.renderer()  # 5 days in the future by default
        today = datetime.now()
        delta = timedelta(1)  # one day
        yesterday = today - delta
        tomorrow = today + delta
        self.assertTrue(render.in_range(today.strftime('%d/%m/%Y')))
        self.assertFalse(render.in_range(yesterday.strftime('%d/%m/%Y')))
        self.assertTrue(render.in_range(tomorrow.strftime('%d/%m/%Y')))

        # TODO: cover dates on next year also; probably mocking datetime.now()
        #       http://nedbatchelder.com/blog/201209/mocking_datetimetoday.html

    def test_get_birthdays_from_users(self):
        render = self.renderer()  # 5 days in the future by default
        # first, we don't have a birthday property on member data
        self.assertEqual(render.get_birthdays_from_users(), [])
        # let's add the property
        memberdata = api.portal.get_tool('portal_memberdata')
        memberdata._setProperty('birthday', '', 'string')
        today = datetime.now()
        properties = dict(birthday=today.strftime('%d/%m/%Y'))
        api.user.create(
            username='foo', email='foo@bar.org', properties=properties)
        # the user birthday's is today, so we got one result
        results = render.get_birthdays_from_users()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['fullname'], 'foo')
        self.assertEqual(
            results[0]['portrait'], 'http://nohost/plone/defaultUser.png')
