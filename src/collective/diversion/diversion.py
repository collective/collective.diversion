diversions = {}

def add_diversion(old, new):
    old = tuple(old.rsplit(".", 1))
    new = tuple(new.rsplit(".", 1))
    if old in diversions:
        data = {'old': ".".join(old), 'first': ".".join(diversions[old]), 'second': ".".join(new), }
        raise ValueError("Two redirects added for %(old)s: \n%(first)s \nand \n%(second)s" % data)
    diversions[old] = new

def rebind_ClassFactory(db):
    old_ClassFactory = db.classFactory
    def ClassFactory(jar, module, name):
        return old_ClassFactory(jar, module, name)
    db.classFactory = ClassFactory
