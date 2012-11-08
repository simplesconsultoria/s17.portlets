# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from s17.portlets.interfaces import IWhitePages


class WhitePages(BrowserView):
    implements(IWhitePages)

    def people_list(self):
        catalog = getToolByName(self.context, 'portal_personcatalog')
        query = {}
        query['fullname'] = self.request.form.get('fullname', '')
        query['review_state'] = ['published', 'internally_published']
        results = catalog.searchResults(**query)
        return results
