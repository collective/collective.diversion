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

