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
        redirected = False
        if (module, name) in diversions:
            redirected = True
            module, name = diversions[module, name]
        kls = old_ClassFactory(jar, module, name)
        if redirected:
            # So, we got the class, but we want its instances to be reporting that it has changed, so it will get
            # persisted into the database. What we REALLY don't want to happen, however, is that the location gets
            # set here rather than the real, replacement class.
            #
            # This means that when you load an object with its old location the first usage will be an ephemeral class
            # defined here that pretends to be the new one. Later loads will be just the new one.
            # 
            # Note: This trick probably won't work with non-persistent objects.
            new_kls = type(kls.__name__, (kls,), {'_p_changed': 1})
            new_kls.__module__ = kls.__module__
            new_kls.__name__ = kls.__name__
            kls = new_kls
        return kls
    db.classFactory = ClassFactory
