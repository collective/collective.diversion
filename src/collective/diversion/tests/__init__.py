from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.testing import z2

class DiversionLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.diversion
        self.loadZCML(package=collective.diversion)
        
        # Install product and call its initialize() function
        z2.installProduct(app, 'collective.diversion')
    
    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'collective.diversion')

FUNCTIONAL_DIVERSION_LAYER = FunctionalTesting(bases=([DiversionLayer()]), name='collective.diversion:functional')
    