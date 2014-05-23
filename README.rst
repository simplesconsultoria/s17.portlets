************
s17.portlets
************

.. contents:: Table of Contents

Life, the Universe, and Everything
==================================

Profile, birthday and white pages portlets for a person.

Mostly Harmless
===============

.. image:: https://secure.travis-ci.org/simplesconsultoria/s17.portlets.png?branch=master
    :alt: Travis CI badge
    :target: http://travis-ci.org/simplesconsultoria/s17.portlets

.. image:: https://coveralls.io/repos/simplesconsultoria/s17.portlets/badge.png?branch=master
    :alt: Coveralls badge
    :target: https://coveralls.io/r/simplesconsultoria/s17.portlets

.. image:: https://pypip.in/d/s17.portlets/badge.png
    :target: https://pypi.python.org/pypi/s17.portlets/
    :alt: Downloads

Got an idea? Found a bug? Let us know by `opening a support ticket`_.

.. _`opening a support ticket`: https://github.com/simplesconsultoria/s17.portlets/issues

Don't panic
===========

Installation
------------

To enable this product in a buildout-based installation:

#. Edit your ``buildout.cfg`` and add ``s17.portlets`` to the list of eggs to
   install ::

    [buildout]
    ...
    eggs =
        s17.portlets

#. Starting on 1.0b2 ``s17.portlets`` no longer depends on ``s17.person``. If
   your project depends on such package, you should add the ``person`` extra
   to your ``buildout.cfg`` or ``setup.py``::

    [buildout]
    ...
    eggs =
        s17.portlets [person]

After updating the configuration you need to run ''bin/buildout'', which will
take care of updating your system.

Go to the 'Site Setup' page in a Plone site and click on the 'Add-ons' link.

Check the box next to ``s17.portlets`` and click the 'Activate' button.

.. Note::
    You may have to empty your browser cache and save your resource registries
    in order to see the effects of the product installation.

Portlets
--------

The following portlets are always available:

**Birthday**
    The birthday portlet displays the names of the persons with upcoming
    birthdays in the following days (the number of days is user configurable).

.. figure:: https://raw.github.com/simplesconsultoria/s17.portlets/master/birthdays.png
    :align: center
    :height: 260px
    :width: 265px

The following portlets currently depend on the installation of `s17.person`_
and work only with Person objects:

**Profile**
    The profile portlet displays information about a person personal profile
    including portrait, resume and latest posts made on the site.

**White pages**
    The white pages portlet displays a search box to look for persons using
    their name.

.. _`s17.person`: https://github.com/simplesconsultoria/s17.person
