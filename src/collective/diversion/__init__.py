from App.config import getConfiguration
from collective.diversion.diversion import rebind_ClassFactory

def initialize(registrar):
    # The ZMI keeps track of what ZODBs have been opened under what names for its Databases tab, grab those DB objects
    mounted_databases = getConfiguration().dbtab.databases
    for db in mounted_databases.values():
        # Switch out the function for resolving a class from an import location with our wrapper
        rebind_ClassFactory(db)
    
