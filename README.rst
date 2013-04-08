collective.diversion
====================

collective.diversion wraps the existing behaviour for broken objects in the ZODB and provides a lookup table that will
be processed in advance of passing down requests. This allows developers to declare old locations of their classes and
have them be automatically and seamlessly migrated to the new code on load.

.. image:: https://secure.travis-ci.org/collective/collective.diversion.png?branch=master
   :target: http://travis-ci.org/collective/collective.diversion

Usage
-----

Simply include the following ZCML declaration in your code::

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:diversion="http://namespaces.plone.org/diversion">

        <diversion:class
            old="Products.example.oldlocation"
            new="collective.example.shiny"
            />

    </configure>

Caveats
-------

Diverted classes will persist their new class when they are written.  However, when ZODB stores references to persistent objects it stores both the oid and the name of the class.  Those class name references will only be updated when the persistent object they are attached to is re-serialised (modified).  Unfortunately this package cannot do this for you as there is no way to find the set of objects which reference a particular object (quickly).  You'll have to leave the diversion directives in your package until you can confirm that all instances and all references have been updated.