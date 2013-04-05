import unittest2 as unittest
from persistent import Persistent
from plone.testing.zodb import EmptyZODB
import transaction

TEST_CLASS_PREFIX = 'testing_data_class_'

class Data(Persistent):
        
    def __init__(self, name, data):
        self.name = name
        self.data = data
    
    def format(self):
        # This method is just to check we have the real class, not just the data
        return self.name, self.data

def get_class():
    classes = sorted((key for key in globals().keys() if key.startswith(TEST_CLASS_PREFIX)), reverse=True)
    
    try:
        newest = classes[0]
    except IndexError:
        newest = TEST_CLASS_PREFIX + "0"
    newest_id = int(newest[len(TEST_CLASS_PREFIX):])
    
    new = TEST_CLASS_PREFIX + str(newest_id + 1)
    globals()[new] = type(new, (Data,), {})
    return globals()[new]

def break_class(name):
    if hasattr(name, "__name__"):
        name = name.__name__
    del globals()[name]
    
class TestSetup(unittest.TestCase):
    layer = EmptyZODB()

    def get_idempotent_root(self):
        conn = self.layer['zodbDB'].open()
        self.conns.append(conn)
        return conn.root()

    def setUp(self):
        self.conns = []
    
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
        
        
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite