#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import has_entry
from hamcrest import assert_that

from nti.app.client_preferences.generations import install

from nti.dataserver.tests.mock_dataserver import WithMockDS
from nti.dataserver.tests.mock_dataserver import mock_db_trans

_user_preferences = """
{
    "webapp_kalturaPreferFlash": true,
    "presence": {
        "active": "available",
        "available": {
            "show": "chat",
            "status": "Back from lunch",
            "type": "available"
        },
        "away": {
            "show": "away",
            "status": "Back from breakfast",
            "type": "available"
        },
        "dnd": {
            "show": "dnd",
            "status": "Back from dinner",
            "type":"available"
        },
        "unavailable": {
            "show": "chat",
            "type": "unavailable"
        }
     }
}"""


from nti.app.client_preferences.tests import PreferenceLayerTest


class TestInstall(PreferenceLayerTest):

    @WithMockDS
    def test_install(self):
        with mock_db_trans() as conn:
            assert_that(conn.root(),
                        has_entry('zope.generations',
                                  has_entry('nti.dataserver:nti.app.client_preferences',
                                            install.generation)))
