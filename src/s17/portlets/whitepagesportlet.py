# -*- coding: utf-8 -*-

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder

from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex

from s17.portlets import PersonPortletsMessageFactory as _


class KeywordsVocabulary(object):
    """Vocabulary factory listing all catalog indexes from the custom catalog
       portal_personcatalog
    """
    implements(IContextSourceBinder)

    def __call__(self, context):
        self.context = context
        self.catalog = api.portal.get_tool('portal_personcatalog')
        if self.catalog is None:
            return SimpleVocabulary([])

        items = []
        for index in self.catalog._catalog.indexes:
            index_type = type(self.catalog._catalog.indexes[index])
            if index_type == ZCTextIndex or index_type == KeywordIndex:
                items.append(index)

        index_list = [SimpleTerm(i, i, i) for i in items]

        return SimpleVocabulary(index_list)


class IWhitePagesPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    portlet_title = schema.TextLine(
        title=_(u"Portlet Title"),
        description=_(u"The portlet title"),
        required=False,
    )

    description = schema.TextLine(
        title=_(u"Portlet description"),
        required=False,
    )


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IWhitePagesPortlet)

    # TODO: Set default values for the configurable parameters here

    portlet_title = u""
    description = u""

    def __init__(self, portlet_title=u"", description=u""):
        self.portlet_title = portlet_title
        self.description = description

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.portlet_title if self.portlet_title else "White Pages"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('whitepagesportlet.pt')

    @property
    def is_anonymous(self):
        """Check if the currently logged-in user is anonymous.

        :returns: True if the current user is anonymous, False otherwise.
        :rtype: bool
        """
        return api.user.is_anonymous()


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IWhitePagesPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IWhitePagesPortlet)
