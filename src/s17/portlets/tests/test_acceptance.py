import unittest

import robotsuite

from plone.testing import layered

from s17.portlets.testing import FUNCTIONAL_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("test_portlets.txt"),
                layer=FUNCTIONAL_TESTING),
    ])
    return suite
