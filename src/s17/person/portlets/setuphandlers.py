from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

def remove_portlets(context):
    site = context.getSite()
    column = getUtility(IPortletManager, name=u'plone.leftcolumn', context=site)
    manager = getMultiAdapter((site, column,), IPortletAssignmentMapping)
    #import pdb;pdb.set_trace()
    #del manager["Assignment-2"] # Login portlet
    #del manager["Assignment-3"] # Recent items portlet