# -*- coding: utf-8 -*-
from plone.testing import layered
from s17.portlets.testing import FUNCTIONAL_TESTING

import doctest
import unittest


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
