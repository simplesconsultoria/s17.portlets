# -*- coding: utf-8 -*-

# BBB: OrderedDict drop-in substitute that works in Python 2.6
try:
    import collections
    OrderedDict = collections.OrderedDict
except AttributeError:
    import ordereddict
    OrderedDict = ordereddict.OrderedDict

from datetime import datetime
from datetime import timedelta
from plone import api
from plone.app.portlets.portlets import base
from plone.memoize import instance
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from s17.portlets import PersonPortletsMessageFactory as _
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

    @instance.memoize
    def _data(self):
        return self.get_birthdays()

    def upcoming_birthdays(self):
        return self._data()

    def get_search_range(self):
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

    def get_birthdays(self):
        """Return next birthdays considering the interval defined in the
        portlet configuration.
        """
        catalog = api.portal.get_tool('portal_personcatalog')
        query = dict(review_state=('published', 'internally_published'))
        birthdays = []
        for range in self.get_search_range():
            query['cooked_birthday'] = {'query': range, 'range': 'minmax'}
            birthdays.extend(catalog.searchResults(**query))
        # sort by date and fullname
        birthdays = [(b.birthday.strftime('%d/%m'), b.Title, b) for b in birthdays]
        birthdays.sort()

        # then deliver an ordered mapping
        results = OrderedDict()
        for b in birthdays:
            day = b[0]
            person = (b[1], b[2])
            if results.get(day):
                results[day] += [person]
            else:
                results[day] = [person]
        return results

    @property
    def available(self):
        """Check if user is not anonymous and if there are any birthdays to
        display.
        """
        return not api.user.is_anonymous() and len(self._data())

    def default_user_portrait(self):
        """Return portal URL."""
        return api.portal.get().absolute_url() + '/defaultUser.png'


class AddForm(base.AddForm):

    """Portlet add form."""

    form_fields = form.Fields(IBirthdayPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    """Portlet edit form."""

    form_fields = form.Fields(IBirthdayPortlet)
