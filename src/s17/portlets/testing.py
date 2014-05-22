# -*- coding: utf-8 -*-
from plone import api
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from s17.portlets.config import HAS_PERSON


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import s17.portlets
        self.loadZCML(package=s17.portlets)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        if HAS_PERSON:
            self.applyProfile(portal, 's17.person:default')
            wt = api.portal.get_tool('portal_workflow')
            wt.setChainForPortalTypes(
                ('Person',), ('simple_publication_workflow',))

        self.applyProfile(portal, 's17.portlets:default')

FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='s17.portlets:Integration',
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, z2.ZSERVER_FIXTURE),
    name='s17.portlets:Functional',
)

ROBOT_TESTING = FunctionalTesting(
    bases=(FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name='s17.portlets:Robot')
