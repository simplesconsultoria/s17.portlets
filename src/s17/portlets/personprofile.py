# -*- coding: utf-8 -*-
from plone import api
from plone.app.portlets.portlets import base
from plone.memoize import instance
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from s17.portlets import PersonPortletsMessageFactory as _
from s17.portlets.utils import get_portrait_url
from zope import schema
from zope.formlib import form
from zope.interface import implements


class IPersonProfile(IPortletDataProvider):

    """Profile portlet.

    Displays a portrait, some useful links and a list of content created by
    the user.
    """

    show_title = schema.Bool(
        title=_(u'Show title'),
        description=_(u'Show title of this portlet.'),
        required=True,
        default=True,
    )

    show_edit_profile_link = schema.Bool(
        title=_(u'Show edit profile link'),
        description=_(u'Show edit profile link for current user.'),
        required=True,
        default=True,
    )

    show_logout_link = schema.Bool(
        title=_(u'Show logout link'),
        description=_(u'Show logout link for current user.'),
        required=True,
        default=True,
    )

    show_recent_content = schema.Bool(
        title=_(u'Show recent content'),
        description=_(u'Show recent content created by current user.'),
        required=True,
        default=True,
    )


class Assignment(base.Assignment):

    """Portlet assignment."""

    implements(IPersonProfile)

    show_title = True
    show_edit_profile_link = True
    show_logout_link = True
    show_recent_content = True

    def __init__(
        self,
        show_title=True,
        show_edit_profile_link=True,
        show_logout_link=True,
        show_recent_content=True,
    ):
        self.show_title = show_title
        self.show_edit_profile_link = show_edit_profile_link
        self.show_logout_link = show_logout_link
        self.show_recent_content = show_recent_content

    @property
    def title(self):
        return _(u'User Profile')


class Renderer(base.Renderer):

    """Portlet renderer."""

    _template = ViewPageTemplateFile('personprofile.pt')

    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        """Check if user is not anonymous."""
        return not api.user.is_anonymous()

    @property
    def show_title(self):
        """Return the value of the show_title field."""
        return self.data.show_title

    @property
    def show_edit_profile_link(self):
        """Return the value of the show_edit_profile_link field."""
        return self.data.show_edit_profile_link

    @property
    def show_logout_link(self):
        """Return the value of the show_logout_link field."""
        return self.data.show_logout_link

    @property
    def show_recent_content(self):
        """Return the value of the show_recent_content field."""
        return self.data.show_recent_content

    @property
    def current_user_id(self):
        """Return the id of the current user."""
        return api.user.get_current().getId()

    @property
    def portrait_url(self):
        """Return the URL of the portrait of the current user."""
        # XXX: This will return always the image of the Plone user and not
        #      the image of the Person object. We should fix s17.person to
        #      synchronize those images.
        return get_portrait_url(self.current_user_id)

    @instance.memoize
    def get_user_content(self):
        """Return a list of content created by the user as catalog brains."""
        self.catalog = api.portal.get_tool('portal_catalog')
        posts = 5
        query = dict(
            Creator=self.current_user_id,
            sort_on='Date',
            sort_order='reverse',
            sort_limit=posts,
        )
        return self.catalog(**query)[:posts]

    @property
    def user_has_content(self):
        """Return True if the user has content created."""
        return len(self.get_user_content()) > 0

    def toLocalizedTime(self, date):
        """Return the localized time of the date."""
        util = api.portal.get_tool('translation_service')
        return util.toLocalizedTime(date, long_format=True)

    @instance.memoize
    def all_user_content_url(self):
        """Return URL of a search of content created by the user."""
        portal_url = api.portal.get().absolute_url()
        search_url = '{0}/search?Creator={1}&sort_on=created&sort_order=reverse'
        return search_url.format(portal_url, self.current_user_id)

    @instance.memoize
    def portal_url(self):
        """Return the URL of the portal."""
        return api.portal.get().absolute_url()


class AddForm(base.AddForm):

    """Portlet add form."""

    form_fields = form.Fields(IPersonProfile)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    """Portlet edit form."""

    form_fields = form.Fields(IPersonProfile)
