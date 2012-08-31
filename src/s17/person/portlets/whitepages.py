# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from s17.person.portlets.interfaces import IWhitePages


class WhitePages(BrowserView):
    implements(IWhitePages)

    def people_list(self):
        catalog = getToolByName(self.context, 'portal_personcatalog')
        form_request = self.request.form

        results = catalog.searchResults(form_request)
        return results
