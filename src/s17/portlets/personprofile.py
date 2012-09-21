# -*- coding: utf-8 -*-

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

import DateTime

from zope.component import getMultiAdapter

from s17.person.portlets import PersonPortletsMessageFactory as _

from collective.person.content.person import IPerson


class IPersonProfile(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.
    portlet_title = schema.TextLine(
        title=_(u"Portlet Title"),
        description=_(u"Title"),
        required=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IPersonProfile)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""
    portlet_title = u""

    # TODO: Add keyword parameters for configurable parameters here
    def __init__(self, portlet_title=u""):
        self.portlet_title = portlet_title

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.portlet_title if self.portlet_title else "Person Profile"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('personprofile.pt')

    def get_user_id(self):
        mt = getToolByName(self.context, 'portal_membership')
        user = mt.getAuthenticatedMember()
        user_id = user.getId()
        return user_id

    def get_user_profile(self):
        user_id = self.get_user_id()
        person = self.get_person(user_id)
        url = ''
        if person:
            url = person.getURL()
        return url

    def get_resume(self):
        return ''

    def get_person(self, user_id):
        self.catalog = getToolByName(self.context, "portal_personcatalog")
        person = self.catalog.searchResults({'id': user_id})
        person = person[0] if person else None

        return person

    def get_portrait(self, width=200):
        #XXX this should be replace by an IPerson data
        user_id = self.get_user_id()

        person = self.get_person(user_id)
        tag = '<img width="75" height="99" title="" alt="" src="defaultUser.png">'

        if person:
            obj = person.getObject()

            image = obj.picture
            if image:
                image_size = image.getImageSize()
                w = image_size[0]
                h = image_size[1]
                proportion = h / float(w)

                height = round(width * proportion, 0)
                images = getMultiAdapter((obj, self.request), name="images")
                img = images.scale('picture', width=width, height=height)
                tag = img.tag()

        return tag

    def get_participation(self):
        user_id = self.get_user_id()

        self.catalog = getToolByName(self.context, "portal_catalog")
        query = {}
        sort_limit = 5
        query['Creator'] = user_id
        query['sort_order'] = 'reverse'
        query['sort_on'] = 'Date'
        query['sort_limit'] = sort_limit
        participation_list = self.catalog.searchResults(query)[:sort_limit]
        return participation_list

    def data_transform(self, date):
        formated_date = DateTime.DateTime(date).strftime('%d/%m/%Y')
        return formated_date

    @property
    def is_anonymous(self):
        """ """
        pm = getToolByName(self.context, 'portal_membership')
        return pm.isAnonymousUser()


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IPersonProfile)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IPersonProfile)
