Changelog
=========

There's a frood who really knows where his towel is.

1.0b2 (2014-06-03)
------------------

.. Warning::
    This release makes the use of ``s17.person`` optional. If your project
    depends on such package, you should add the ``person`` extra to your
    Buildout configuration or ``setup.py``. See package documentation for more
    information.

- Brazilian Portuguese and Spanish translations were updated.
  [hvelarde]

- The User Profile portlet was completely refactored and will only work with
  users and not with ``s17.person`` objects as it doesn't make sense.
  [hvelarde]

- The Birthdays portlet was completely refactored. If ``s17.person`` is
  installed, it will use the ``birthday`` field on the content type to
  grab the upcoming birthdays using the Person catalog; otherwise, it will
  look for a user defined ``birthday`` field on the MemberData tool.
  [hvelarde]

- The package ``s17.person`` is no longer a hard dependency, but an extra
  requirement.
  [hvelarde]


1.0b1 (2012-09-21)
------------------

- Deprecate use on Plone 4.1; we will support only Plone >=4.2. [hvelarde]

- Rename package from s17.person.portlets to s17.portlets. [hvelarde]

- Add description field. [aleGpereira]

- Limit list of participations in profile portlet to five. [aleGpereira]

- Make results of white pages appear in a overlay. [aleGpereira]

- Improves birthday portlet [davilima6]

- Group birthdays by day and also sort them by fullname [davilima6]

- Add small portrait for each person with a birthday [davilima6]


1.0a5 (2012-08-07)
------------------

- Fixed tests in get_participation function in person portlet [lepri]

- Added overlay in search person [lepri]

- Fixed query in person profile portlet [lepri]

- Adding test case for portlets with anonymous users. [aleGpereira]

- Improve the products translation [lepri]


1.0a4 (2012-06-27)
------------------

- Set render view and template properly for anonymous users in portlets.
  [aleGpereira]


1.0a3 (2012-06-14)
------------------

- Fixed package distribution. [hvelarde]


1.0a2 (2012-06-13)
------------------

- Added uninstall profile. [aleGpereira]


1.0a1 (2012-05-21)
------------------

- Initial release.
