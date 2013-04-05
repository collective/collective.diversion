from collective.diversion.diversion import rebind_ClassFactory

def initialize(registrar):
    db = registrar._ProductContext__app._p_jar.db()
    rebind_ClassFactory(db)