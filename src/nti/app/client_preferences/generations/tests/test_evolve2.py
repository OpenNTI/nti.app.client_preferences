#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import none
from hamcrest import assert_that

import fudge

import simplejson as json

from zope.preference import interfaces as pref_interfaces

from zope.security.interfaces import IPrincipal
from zope.security.management import newInteraction, endInteraction

from nti.app.client_preferences.generations.evolve2 import evolve
from nti.app.client_preferences.generations.evolve2 import _Participation

from nti.base.deprecation import hides_warnings

from nti.dataserver.utils.example_database_initializer import ExampleDatabaseInitializer

from nti.dataserver.tests.mock_dataserver import mock_db_trans, WithMockDS

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


class TestEvolve2(PreferenceLayerTest):

    @hides_warnings
    @WithMockDS
    def test_evolve2(self):
        key = 'nti.dataserver.users.preferences.EntityPreferences'
        with mock_db_trans() as conn:
            context = fudge.Fake().has_attr(connection=conn)
            initializer = ExampleDatabaseInitializer(max_test_users=5, skip_passwords=True)
            initializer.install(context)

            ds_folder = context.connection.root()['nti.dataserver']
            user = ds_folder['users']['jason.madden']
            annotations = user.__annotations__
            prefs = annotations[key] = {}
            prefs.update(json.loads(_user_preferences))

        with mock_db_trans() as conn:
            context = fudge.Fake().has_attr(connection=conn)
            evolve(context)

        with mock_db_trans() as conn:
            ds_folder = context.connection.root()['nti.dataserver']
            user = ds_folder['users']['jason.madden']

            ep = user.__annotations__.get(key, None)
            assert_that(ep, is_(none()))

            principal = IPrincipal(user)
            newInteraction(_Participation(principal))

            root_prefs = pref_interfaces.IUserPreferences(user)
            assert_that(root_prefs.WebApp.preferFlashVideo, is_(True))

            assert_that(root_prefs.ChatPresence.Active.status,
                        is_('Back from lunch'))
            assert_that(root_prefs.ChatPresence.Available.status,
                        is_('Back from lunch'))
            assert_that(root_prefs.ChatPresence.Away.status,
                        is_('Back from breakfast'))
            assert_that(root_prefs.ChatPresence.DND.status,
                        is_('Back from dinner'))

            endInteraction()
