import unittest2 as unittest

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
#from plone.app.testing import IntegrationTesting
from plone.testing import z2
from plone.testing import zca

from collective.diversion import diversion

class DiversionLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.diversion
        self.loadZCML(package=collective.diversion)
        
        # Install product and call its initialize() function
        z2.installProduct(app, 'collective.diversion')
    
    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'collective.diversion')
    

class TestZCML(unittest.TestCase):
    layer = DiversionLayer()
    
    def test_adding_class_declaration(self):
        # Create a new global registry
        zca.pushGlobalRegistry()

        from zope.configuration import xmlconfig
        self.layer['configurationContext'] = context = zca.stackConfigurationContext(self.layer.get('configurationContext'))
        xmlconfig.string("""\
            <configure
                xmlns="http://namespaces.zope.org/zope"
                xmlns:diversion="http://namespaces.plone.org/diversion">
                
                <diversion:class
                    old="Products.example.oldlocation"
                    new="collective.example.shiny"
                    />

            </configure>
            
        """, context=context)
        try:
            self.assertEqual(diversion.diversions, {('Products.example', 'oldlocation'): ('collective.example', 'shiny')})
        finally:
            del self.layer['configurationContext']
        
    
    def test_loading_zcml_wraps_classFactory(self):
        # We need the classFactory to be our one for this to actually do anything
        # It is set up as a side-effect of installing the product. Hopefully this happens late enough for all other
        # customisations to this setting to have been processed.
        # 
        # If there are problems on startup then you'll want to make this happen earlier, but I've not seen any failure
        # modes like that
        self.assertEqual(self.layer['zodbDB'].classFactory.__module__, 'collective.diversion.diversion')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestZCML))
    return suite
