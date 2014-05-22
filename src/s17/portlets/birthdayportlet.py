# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from plone import api
# from plone.app.portlets.cache import render_cachekey
from plone.app.portlets.portlets import base
from plone.memoize import instance
# from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from s17.portlets import PersonPortletsMessageFactory as _
from s17.portlets.config import HAS_PERSON
from s17.portlets.utils import get_portrait_url
from s17.portlets.utils import sort_birthdays
from zope import schema
from zope.formlib import form
from zope.interface import implements


class IBirthdayPortlet(IPortletDataProvider):

    """Birthday portlet.

    It displays the date, portrait and name of the persons that have
    aniversaries in the following days.
    """

    days_number = schema.Int(
        title=_(u'Days'),
        description=_(u'Search for birthdays from here plus numbers of days'),
        default=30,
        required=True,
    )


class Assignment(base.Assignment):

    """Portlet assignment."""

    implements(IBirthdayPortlet)

    def __init__(self, days_number=30):
        self.days_number = days_number

    @property
    def title(self):
        return _(u'Birthdays')


class Renderer(base.Renderer):

    """Portlet renderer."""

    _template = ViewPageTemplateFile('birthdayportlet.pt')

    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        """Check if user is not anonymous and if there are any birthdays to
        display.
        """
        return not api.user.is_anonymous() and len(self._data())

    @instance.memoize
    def _data(self):
        """Return birthdays sorted by day an fullname."""
        if HAS_PERSON:
            birthdays = self.get_birthdays_from_persons()
        else:
            birthdays = self.get_birthdays_from_users()
        return sort_birthdays(birthdays)

    def upcoming_birthdays(self):
        return self._data()

    def get_search_range(self):
        """Return a list of search range tuples to be used to get birthdays
        from a person catalog.
        """
        today = datetime.now()
        future = today + timedelta(days=self.data.days_number)
        next_year = future.year > today.year

        today, future = today.strftime('%m%d'), future.strftime('%m%d')
        ranges = []
        if next_year:
            ranges.append((today, '1231'))
            ranges.append(('0101', future))
        else:
            ranges.append((today, future))
        return ranges

    def get_birthdays_from_persons(self):
        """Return next birthdays considering the interval defined in the
        portlet configuration.

        Birthday items include the following information:
        - birthday: day and month
        - fullname: full name of the person
        - description: description of the person
        - url: absolute url of the Person object
        - portrait: absolute url of the person portrait

        :returns: list of persons information
        :rtype: list of dict
        """
        catalog = api.portal.get_tool('portal_personcatalog')
        query = dict(
            review_state=('published', 'internally_published'),
            sort_on='cooked_birthday',
        )
        birthdays = []
        for range in self.get_search_range():
            query['cooked_birthday'] = {'query': range, 'range': 'minmax'}
            birthdays.extend(catalog.searchResults(**query))

        results = []
        for brain in birthdays:
            person = brain.getObject()
            results.append(dict(
                birthday=person.birthday.strftime('%d/%m'),  # remove the year
                fullname=person.title,
                description=person.description,
                url=person.absolute_url(),
                portrait=get_portrait_url(person),
            ))
        return results

    def in_range(self, date):
        """Return True if the date is in the range from today to the number
        of days especified in the portlet configuration.

        :param date: [required] date to be checked againts range.
        :type date: string
        :returns: True if the date is in range, False otherwise.
        :rtype: bool
        """
        try:
            target = datetime.strptime(date, '%d/%m/%Y')
        except ValueError:
            return False  # the string does not match format
        target = target.strftime('%m%d')
        in_range = False
        for start, end in self.get_search_range():
            in_range |= start <= target <= end
        return in_range

    def get_birthdays_from_users(self):
        """Return next user birthdays considering the interval defined in
        the portlet configuration. Birthday information is taken from
        `portal_memberdata` and we need to add a field called `birthday`.
        This is the preferred method if `s17.person` is not installed.

        Birthday items include the following information:
        - birthday: day and month
        - fullname: full name of the user
        - description: description of the user
        - url: absolute url of the author's page
        - portrait: absolute url of the user portrait

        :returns: list of users information
        :rtype: list of dict
        """
        results = []
        memberdata = api.portal.get_tool('portal_memberdata')
        if not memberdata.hasProperty('birthday'):
            return results

        portal_url = api.portal.get().absolute_url()
        users = api.user.get_users()
        users = [u for u in users if self.in_range(u.getProperty('birthday'))]
        for u in users:
            results.append(dict(
                birthday=u.getProperty('birthday')[:-5],  # remove the year
                fullname=u.getProperty('fullname') or u.getId(),
                description=u.getProperty('description'),
                url=portal_url + '/author/' + u.getId(),
                portrait=get_portrait_url(u.getId()),
            ))
        return results


class AddForm(base.AddForm):

    """Portlet add form."""

    form_fields = form.Fields(IBirthdayPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    """Portlet edit form."""

    form_fields = form.Fields(IBirthdayPortlet)
