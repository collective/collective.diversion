from zope.interface import Interface 
from zope.schema import TextLine
  
class IClassDiversion(Interface): 
    """Redirects loads for a persistent class to a specified import location"""
   
    old = TextLine( 
        title=u"Old location",
        description=u"The original place this was when it was persisted",
        required=True)
    
    new = TextLine(
        title=u"New location",
        description=u"Where it has moved to",
        required=True)
    
