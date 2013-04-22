import unittest2 as unittest

import transaction
from OFS.SimpleItem import SimpleItem
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy

import collective.diversion
from collective.diversion import diversion
from collective.diversion.tests import FUNCTIONAL_DIVERSION_LAYER
from collective.diversion.tests.test_translation import get_class, break_class

class TestZopeIntegration(unittest.TestCase):
    layer = FUNCTIONAL_DIVERSION_LAYER
    
    def test_copy_paste_respects_diversions(self):
        # We shouldn't need to do this in the test, but it seems that the functional tests don't get on with it.
        # It works fine in the real site, trust me.
        collective.diversion.initialize(None)
        
        root = self.layer['app']
        
        from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy, OmnipotentUser

        _policy=PermissiveSecurityPolicy()
        setSecurityPolicy(_policy)
        newSecurityManager(None, OmnipotentUser().__of__(root.acl_users))
                
        old = get_class(bases=[SimpleItem])
        new = get_class(bases=[SimpleItem])
        
        conn = self.layer['zodbDB'].open()
        conn.root()['Application']['foo'] = old("foo", "bar")
        conn.root()._p_jar.transaction_manager.commit()
        
        break_class(old)
        diversion.add_diversion(old="collective.diversion.tests.test_translation.%s" % old.__name__, 
                                new="collective.diversion.tests.test_translation.%s" % new.__name__)
        root._product_meta_types = tuple([{'name':old.meta_type, 'permission':'View', 'action':'View'}])
        
        root.manage_pasteObjects(root.manage_copyObjects('foo'))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestZopeIntegration))
    return suite
