# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

# TODO: If you define any fields for the portlet configuration schema below
# do not forget to uncomment the following import
from zope import schema
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from collective.person.content.person import IPerson

# TODO: If you require i18n translation for any of your schema fields below,
# uncomment the following to import your package MessageFactory
from s17.person.portlets import PersonPortletsMessageFactory as _


class IBirthdayPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    portlet_title = schema.TextLine(title=_(u"Portlet Title"),
                                  description=_(u"the Title of the portlet"),
                                  required=True)

    days_number = schema.Int(title=_(u"Numbers of days"),
                                  description=_(u"Search for birthdays from \
                                  here plus numbers of days"),
                                  required=True,
                                  default=0)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IBirthdayPortlet)

    # TODO: Set default values for the configurable parameters here

    portlet_title = u""
    days_number = 0

    # TODO: Add keyword parameters for configurable parameters here
    def __init__(self, portlet_title=u"", days_number=0):
        self.portlet_title = portlet_title
        self.days_number = days_number

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.portlet_title if self.portlet_title else \
               "Birthday Portlet"


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
        is_other_year = future_date.month < now.month
        if is_other_year:
            results.append((today, '1231'))
            results.append(('0101', future))
        else:
            results.append((today, future))
        return results

    def get_birthdays(self):
        birthdays = None
        self.catalog = getToolByName(self.context, "portal_personcatalog")
        ranges = self.get_search_range()
        for search_range in ranges:
            query = {}
            query['cooked_birthday'] = {'query': search_range,
                                        'range': 'minmax'}
            query['sort_order'] = 'birthday'
            query['object_provides'] = {'query': [IPerson.__identifier__]}
            if birthdays:
                birthdays = birthdays + \
                                 self.catalog.searchResults(query)
            else:
                birthdays = self.catalog.searchResults(query)

        return birthdays

    def toLocalizedTime(self, date):
        toLocalizedTime = self.context.restrictedTraverse('@@plone').toLocalizedTime
        toLocalizedTime = toLocalizedTime(date.strftime('%m/%d')).rsplit('/', 1)[0]
        return toLocalizedTime

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
