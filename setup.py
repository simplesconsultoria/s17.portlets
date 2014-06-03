# -*- coding:utf-8 -*-
from setuptools import find_packages
from setuptools import setup

version = '1.0b2'
long_description = (
    open('README.rst').read() + '\n' +
    open('CONTRIBUTORS.rst').read() + '\n' +
    open('CHANGES.rst').read()
)

setup(name='s17.portlets',
      version=version,
      description="User Profile, Birthdays and White Pages portlets for a user or person.",
      long_description=long_description,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Office/Business",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='user person profile birthdays search portlet',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='https://github.com/simplesconsultoria/s17.portlets',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['s17'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'five.grok',
          'ordereddict >=1.1',  # BBB: OrderedDict substitute for Python 2.6
          'plone.api',
          'plone.app.portlets',
          'plone.memoize',
          'plone.portlets',
          'Products.CMFCore',
          'Products.CMFPlone >=4.2',
          'Products.GenericSetup',
          'Products.ZCTextIndex',
          'setuptools',
          'zope.component',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
      ],
      extras_require={
          'person': [
              's17.person',
          ],
          'test': [
              'plone.app.referenceablebehavior',
              'plone.app.robotframework',
              'plone.app.testing [robot] >=4.2.2',
              'plone.namedfile [blobs]',
              'plone.testing',
              'robotsuite',
          ],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
