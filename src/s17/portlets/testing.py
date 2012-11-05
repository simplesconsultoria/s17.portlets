# -*- coding: utf-8 -*-

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.testing.z2 import ZSERVER_FIXTURE

class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import s17.portlets
        self.loadZCML(package=s17.portlets)
        # Load ZCML
        import s17.person
        self.loadZCML(package=s17.person)
        #XXX: We should not have this here but...
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        import plone.app.referenceablebehavior
        self.loadZCML(package=plone.app.referenceablebehavior)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 's17.portlets:default')
        self.applyProfile(portal, 's17.person:default')


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='s17.portlets:Integration',
    )
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, ZSERVER_FIXTURE,),
    name='s17.portlets:Functional',
    )
