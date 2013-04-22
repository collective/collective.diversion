from App.config import getConfiguration
from collective.diversion.diversion import DivertingUnpickler, rebind_ClassFactory
from cPickle import Unpickler

def initialize(registrar):
    # The ZMI keeps track of what ZODBs have been opened under what names for its Databases tab, grab those DB objects
    mounted_databases = getConfiguration().dbtab.databases
    for db in mounted_databases.values():
        try:
            # Some code wraps the DB in a facade before passing it to the dbtab
            # They pass .open calls through, so use this to reclaim the original DB
            db = db.open.im_self
        except AttributeError:
            pass
        # Switch out the function for resolving a class from an import location with our wrapper
        rebind_ClassFactory(db)
    
    import ZODB.ExportImport
    ZODB.ExportImport.Unpickler = DivertingUnpickler
    
