# -*- coding: utf-8 -*-
import pkg_resources

try:
    pkg_resources.get_distribution('s17.person')
except pkg_resources.DistributionNotFound:
    HAS_PERSON = False
else:
    HAS_PERSON = True

PROJECTNAME = 's17.portlets'
