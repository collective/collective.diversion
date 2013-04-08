diversions = {}

def add_diversion(*args, **kwargs):
    if 'old' not in kwargs or 'new' not in kwargs:
        raise ValueError("You must provide new and old locations as dotted names")
    old = kwargs['old']
    new = kwargs['new']
    old = tuple(old.rsplit(".", 1))
    new = tuple(new.rsplit(".", 1))
    if old in diversions:
        if diversions[old] == new:
            return
        data = {'old': ".".join(old), 'first': ".".join(diversions[old]), 'second': ".".join(new), }
        raise ValueError("Two redirects added for %(old)s: \n%(first)s \nand \n%(second)s" % data)
    diversions[old] = new

def rebind_ClassFactory(db):
    old_ClassFactory = db.classFactory
    def ClassFactory(jar, module, name):
        if (module, name) in diversions:
            module, name = diversions[module, name]
        return old_ClassFactory(jar, module, name)

    def rebind_ObjectReader(connection):
        """Connections set up ObjectReaders on init which cache a reference to the classfactory. We are binding later
        so we try to recreate these objectreader objects to use the new factory"""
        connection._reader._factory = ClassFactory

    db.pool.all.map(rebind_ObjectReader)
    db.classFactory = ClassFactory
