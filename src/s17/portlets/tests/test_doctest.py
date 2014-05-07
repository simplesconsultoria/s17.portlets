# -*- coding: utf-8 -*-
import unittest2 as unittest
import doctest

from plone.testing import layered

from s17.portlets.testing import FUNCTIONAL_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            doctest.DocFileSuite(
                'tests/portlets_with_anonymous.txt', package='s17.portlets'),
            layer=FUNCTIONAL_TESTING
        ),
    ])
    return suite
