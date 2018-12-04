# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import imio.ws.register


class ImioWsRegisterLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        self.loadZCML(package=imio.ws.register)


IMIO_WS_REGISTER_FIXTURE = ImioWsRegisterLayer()


IMIO_WS_REGISTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IMIO_WS_REGISTER_FIXTURE,),
    name='ImioWsRegisterLayer:IntegrationTesting',
)


IMIO_WS_REGISTER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IMIO_WS_REGISTER_FIXTURE,),
    name='ImioWsRegisterLayer:FunctionalTesting',
)


IMIO_WS_REGISTER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        IMIO_WS_REGISTER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='ImioWsRegisterLayer:AcceptanceTesting',
)
