# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from zope.interface import implements

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from s17.portlets.interfaces import IWhitePages


class WhitePages(BrowserView):
    implements(IWhitePages)

    def __init__(self, context, request):
        super(WhitePages, self).__init__(context, request)
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.catalog = getToolByName(self.context, 'portal_personcatalog')

    def people_list(self):
        catalog = getToolByName(self.context, 'portal_personcatalog')
        self.fullname = self.request.form.get('fullname', '')
        query = {}
        query['fullname'] = self.fullname
        query['review_state'] = ['published', 'internally_published']
        results = catalog.searchResults(**query)
        return results

    def get_parents(self, person, parents=None):
        try:
            from s17.organizationalunit.content.organizationalunit import \
                IOrganizationalUnit
        except ImportError:
            return None
        parent = person.getObject().__parent__
        if IOrganizationalUnit.providedBy(parent):
            view = parent.unrestrictedTraverse('@@view')
            parents = view.get_parents(full_path=True)
        return parents
