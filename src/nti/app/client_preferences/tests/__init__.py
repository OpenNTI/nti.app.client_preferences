#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""


.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from nti.testing.layers import ZopeComponentLayer
from nti.testing.layers import ConfiguringLayerMixin
import zope.testing.cleanup
from nti.dataserver.tests.mock_dataserver import DataserverLayerTest
from nti.dataserver.tests.mock_dataserver import DSInjectorMixin

class PreferenceLayer(ZopeComponentLayer,
					  ConfiguringLayerMixin,
					  DSInjectorMixin):

	set_up_packages = ('nti.dataserver',
					   'nti.app.client_preferences',
					   ('test_preferences_views.zcml', 'nti.app.client_preferences.tests'),)

	@classmethod
	def setUp(cls):
		cls.setUpPackages()

	@classmethod
	def tearDown(cls):
		cls.tearDownPackages()
		zope.testing.cleanup.cleanUp()

	@classmethod
	def testSetUp(cls):
		pass

	@classmethod
	def testTearDown(cls):
		pass

import unittest
class PreferenceLayerTest(DataserverLayerTest):
	layer = PreferenceLayer
