import copy
import unittest2 as unittest
from persistent import Persistent
from plone.testing.zodb import EmptyZODB
import transaction

from collective.diversion import diversion

TEST_CLASS_PREFIX = 'testing_data_class_'

class Data(Persistent):
        
    def __init__(self, name, data):
        self.name = name
        self.data = data
    
    def format(self):
        # This method is just to check we have the real class, not just the data
        return self.name, self.data

class NPData(object):
        
    def __init__(self, name, data):
        self.name = name
        self.data = data
    
    def format(self):
        # This method is just to check we have the real class, not just the data
        return self.name, self.data

def get_class(base=Data):
    classes = sorted((key for key in globals().keys() if key.startswith(TEST_CLASS_PREFIX)), reverse=True)
    
    try:
        newest = classes[0]
    except IndexError:
        newest = TEST_CLASS_PREFIX + "0"
    newest_id = int(newest[len(TEST_CLASS_PREFIX):])
    
    new = TEST_CLASS_PREFIX + str(newest_id + 1)
    globals()[new] = type(new, (base,), {})
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
    
    @unittest.expectedFailure
    def test_once_loaded_the_first_time_the_new_path_is_used_forever(self):
        root = self.layer['zodbRoot']
        old = get_class()
        new = get_class()
        root['foo'] = old("foo", "bar")
        transaction.commit()
        
        break_class(old)
        diversion.add_diversion(old="collective.diversion.tests.test_translation.%s" % old.__name__, 
                                new="collective.diversion.tests.test_translation.%s" % new.__name__)
        
        foo = self.get_idempotent_root()['foo']
        # Commit in the new transaction, which should be transparently migrating
        foo._p_jar.transaction_manager.commit()
        
        # Forcibly clear the diversion table, so if the database has the original location it will error
        diversion.diversions.clear()
        
        foo = self.get_idempotent_root()['foo']
        self.assertEqual(foo.name, "foo")
        self.assertEqual(foo.data, "bar")
        self.assertEqual(foo.format(), ("foo","bar"))
    
    @unittest.expectedFailure
    def test_moving_non_persistent_objects_doesnt_cause_p_changed_setting_to_be_persisted(self):
        root = self.layer['zodbRoot']
        old = get_class(base=NPData)
        new = get_class(base=NPData)
        root['foo'] = old("foo", "bar")
        self.assertFalse(hasattr(root['foo'], "_p_changed"))
        transaction.commit()
        
        break_class(old)
        diversion.add_diversion(old="collective.diversion.tests.test_translation.%s" % old.__name__, 
                                new="collective.diversion.tests.test_translation.%s" % new.__name__)
        
        new_root = self.get_idempotent_root()
        # Commit in the new transaction, which should be transparently migrating
        new_root._p_jar.transaction_manager.commit()
        
        # We shouldn't have a _p_changed as this should be loading from the new location, not an ephemeral class
        foo = self.get_idempotent_root()['foo']
        self.assertFalse(hasattr(foo, "_p_changed"))
        self.assertEqual(foo.name, "foo")
        self.assertEqual(foo.data, "bar")
        self.assertEqual(foo.format(), ("foo","bar"))
    

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