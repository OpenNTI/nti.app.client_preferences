#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import has_entry
from hamcrest import assert_that

from nti.app.client_preferences.generations import install

from nti.app.client_preferences.tests import PreferenceLayerTest

from nti.dataserver.tests.mock_dataserver import WithMockDS
from nti.dataserver.tests.mock_dataserver import mock_db_trans


class TestInstall(PreferenceLayerTest):

    @WithMockDS
    def test_install(self):
        with mock_db_trans() as conn:
            assert_that(conn.root(),
                        has_entry('zope.generations',
                                  has_entry('nti.dataserver:nti.app.client_preferences',
                                            install.generation)))
