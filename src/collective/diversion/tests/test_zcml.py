import unittest2 as unittest

from plone.app.testing.layers import PLONE_INTEGRATION_TESTING
from plone.testing import zca
from plone.testing import Layer

import collective.diversion
from collective.diversion import diversion

ZCML_SANDBOX = zca.ZCMLSandbox(filename="meta.zcml", package=collective.diversion)


class DiversionLayer(Layer):    
    defaultBases = (ZCML_SANDBOX, PLONE_INTEGRATION_TESTING)
    

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

        self.assertEqual(diversion.diversions, {('Products.example', 'oldlocation'): ('collective.example', 'shiny')})
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestZCML))
    return suite
