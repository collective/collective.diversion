import unittest2 as unittest
from persistent import Persistent
from plone.testing.zodb import EmptyZODB
import transaction

TEST_CLASS_PREFIX = 'testing_data_class_'

class Data(Persistent):
        
    def __init__(self, name, data):
        self.name = name
        self.data = data
    

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

    def setUp(self):
        root = self.layer['zodbRoot']
    
    def test_creating_class(self):
        root = self.layer['zodbRoot']
        kls = get_class()
        root['foo'] = kls("foo", "bar")
        transaction.commit()
        self.assertEqual(root['foo'].name, "foo")
        self.assertEqual(root['foo'].data, "bar")
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite