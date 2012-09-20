# -*- coding: utf-8 -*-

try:
    from collections import OrderedDict
# not available on Python < 2.7
except ImportError:
    from ordereddict import OrderedDict

from datetime import datetime, timedelta

from zope.interface import implements
from zope import schema
from zope.formlib import form

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from collective.person.content.person import IPerson

from s17.person.portlets import PersonPortletsMessageFactory as _


class IBirthdayPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    portlet_title = schema.TextLine(title=_(u"Portlet Title"),
                                  description=_(u"the Title of the portlet"),
                                  required=True)

    days_number = schema.Int(title=_(u"Numbers of days"),
                                  description=_(u"Search for birthdays from \
                                  here plus numbers of days"),
                                  required=True,
                                  default=30)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IBirthdayPortlet)

    # TODO: Set default values for the configurable parameters here

    portlet_title = u""
    days_number = 30

    # TODO: Add keyword parameters for configurable parameters here
    def __init__(self, portlet_title=u"", days_number=30):
        self.portlet_title = portlet_title
        self.days_number = days_number

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.portlet_title if self.portlet_title else \
               _("Birthday Portlet")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    def get_search_range(self):
        results = []
        now = datetime.now()
        future_date = now + timedelta(days=self.data.days_number)
        today = now.strftime('%m%d')
        future = future_date.strftime('%m%d')
        is_other_year = False
        if future_date.month == now.month:
            if future_date.day <= now.day:
                is_other_year = True
        elif future_date.month < now.month:
            is_other_year = True

        if is_other_year:
            results.append((today, '1231'))
            results.append(('0101', future))
        else:
            results.append((today, future))
        return results

    def get_birthdays(self):

        # get next birthdays considering the interval defined in the portlet
        birthdays = None
        self.catalog = getToolByName(self.context, 'portal_personcatalog')
        ranges = self.get_search_range()
        for search_range in ranges:
            query = {}
            query['cooked_birthday'] = {'query': search_range,
                                        'range': 'minmax'}
            query['sort_on'] = 'birthday'
            query['object_provides'] = {'query': [IPerson.__identifier__]}
            if birthdays:
                birthdays = birthdays + \
                                 self.catalog.searchResults(**query)
            else:
                birthdays = self.catalog.searchResults(**query)
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
        """ Checks if user is not anonymous and if there are any
            birthdays to display
        """
        available = self.get_birthdays() and not self.is_anonymous
        return available

    @property
    def is_anonymous(self):
        """ """
        pm = getToolByName(self.context, 'portal_membership')
        return pm.isAnonymousUser()

    render = ViewPageTemplateFile('birthdayportlet.pt')


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IBirthdayPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IBirthdayPortlet)
