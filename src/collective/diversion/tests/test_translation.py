import copy
import unittest2 as unittest
from persistent import Persistent
from plone.testing.zodb import EmptyZODB
import transaction

from collective.diversion import diversion

TEST_CLASS_PREFIX = 'testing_data_class_'

class Data(Persistent):
        
    def __init__(self, name, data):
        self.id = name
        self.data = data
    
    @property
    def name(self):
        return self.id
    
    def format(self):
        # This method is just to check we have the real class, not just the data
        return self.name, self.data

def get_class(bases=None):
    classes = sorted((key for key in globals().keys() if key.startswith(TEST_CLASS_PREFIX)), reverse=True)
    
    try:
        newest = classes[0]
    except IndexError:
        newest = TEST_CLASS_PREFIX + "0"
    newest_id = int(newest[len(TEST_CLASS_PREFIX):])
    
    new = TEST_CLASS_PREFIX + str(newest_id + 1)
    if bases is None:
        bases = (Data, )
    else:
        bases = (Data, ) + tuple(bases)
    globals()[new] = type(new, bases, {})
    return globals()[new]

def break_class(name):
    if hasattr(name, "__name__"):
        name = name.__name__
    del globals()[name]
    
class TestZODB(unittest.TestCase):
    layer = EmptyZODB()

    def get_idempotent_root(self):
        conn = self.layer['zodbDB'].open()
        self.conns.append(conn)
        return conn.root()

    def setUp(self):
        self.conns = []
        diversion.rebind_ClassFactory(self.layer['zodbDB'])
        pass
    
    def test_creating_class(self):
        root = self.layer['zodbRoot']
        kls = get_class()
        root['foo'] = kls("foo", "bar")
        transaction.commit()
        
        foo = self.get_idempotent_root()['foo']
        self.assertEqual(foo.name, "foo")
        self.assertEqual(foo.data, "bar")
        self.assertEqual(foo.format(), ("foo","bar"))
        self.assertEqual(foo.__class__, kls)
    
    def test_breaking_a_class_causes_a_broken_object(self):
        root = self.layer['zodbRoot']
        kls = get_class()
        root['foo'] = kls("foo", "bar")
        transaction.commit()

        break_class(kls)

        foo = self.get_idempotent_root()['foo']
        with self.assertRaises(AttributeError):
            foo.name
        with self.assertRaises(AttributeError):
            foo.data
        with self.assertRaises(AttributeError):
            foo.format()


    def test_redirector_causes_broken_object_to_be_found(self):
        root = self.layer['zodbRoot']
        old = get_class()
        new = get_class()
        root['foo'] = old("foo", "bar")
        transaction.commit()
        
        break_class(old)
        diversion.add_diversion(old="collective.diversion.tests.test_translation.%s" % old.__name__, 
                                new="collective.diversion.tests.test_translation.%s" % new.__name__)
        
        foo = self.get_idempotent_root()['foo']
        self.assertEqual(foo.name, "foo")
        self.assertEqual(foo.data, "bar")
        self.assertEqual(foo.format(), ("foo","bar"))
        self.assertEqual(foo.__class__, new)
        
        unreleated = get_class()
        self.assertNotEqual(foo.__class__, unreleated)
    
    def test_redirector_still_loaded_in_connections_that_were_opened_before_patching(self):
        root = self.layer['zodbRoot']
        old = get_class()
        new = get_class()
        
        new_root = self.get_idempotent_root()
        new_root['foo'] = old("foo", "bar")
        new_root._p_jar.transaction_manager.commit()
        
        break_class(old)
        diversion.add_diversion(old="collective.diversion.tests.test_translation.%s" % old.__name__,
                                new="collective.diversion.tests.test_translation.%s" % new.__name__)
        
        foo = root['foo']
        self.assertEqual(foo.name, "foo")
        self.assertEqual(foo.data, "bar")
        self.assertEqual(foo.format(), ("foo","bar"))
        self.assertEqual(foo.__class__, new)
        
        unreleated = get_class()
        self.assertNotEqual(foo.__class__, unreleated)
    
    def test_redirected_objects_persist_as_their_new_class(self):
        root = self.layer['zodbRoot']
        old = get_class()
        new = get_class()
        
        # Create an (old) object
        root['foo'] = old("foo","bar")
        transaction.commit()
        
        # Install the diversion
        break_class(old)
        diversion.add_diversion(old="collective.diversion.tests.test_translation.%s" % old.__name__,
                                new="collective.diversion.tests.test_translation.%s" % new.__name__)
        
        # Load the redirected object
        root = self.get_idempotent_root()
        foo = root['foo']
        
        # Modify the redirected object causing it to be re-serialised, this could also
        # be achieved by setting _p_changed, but this is closer to a real world case.
        foo.data = "horses"
        transaction.commit()

        # Keep a reference to the object oid so we can confirm it's correct (see below)
        oid = foo._p_oid

        # Remove the diversions
        diversion.diversions.clear()

        # References to persistent objects are normally stored along with a 
        # named reference to their class.  This means we can't load the object
        # via the root as it still contains a reference to the old class.  Instead,
        # we load the object up directly via oid.
        connection = self.layer['zodbDB'].open()
        foo = connection.get(oid)

        self.assertEqual(foo.__class__,new)
    

class TestRedirector(unittest.TestCase):

    def test_adding_path_adds_to_translation_table(self):
        old_length = len(diversion.diversions)
        diversion.add_diversion(old="foo.bar.baz", new="example.spam.eggs")
        new_length = len(diversion.diversions)
        
        self.assertEqual(old_length + 1, new_length)

    def test_readding_exact_translation_is_a_noop(self):
        diversion.add_diversion(old="foo.bar.baz", new="example.spam.eggs")
        old_translations = copy.copy(diversion.diversions)
        
        diversion.add_diversion(old="foo.bar.baz", new="example.spam.eggs")
        self.assertEqual(old_translations, diversion.diversions)
            
    def test_readding_differing_translation_causes_error(self):
        diversion.add_diversion(old="foo.bar.baz", new="example.spam.eggs")
        old_translations = copy.copy(diversion.diversions)
        
        with self.assertRaises(ValueError):
            diversion.add_diversion(old="foo.bar.baz", new="example.spam.chips")
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestZODB))
    suite.addTest(unittest.makeSuite(TestRedirector))
    return suite