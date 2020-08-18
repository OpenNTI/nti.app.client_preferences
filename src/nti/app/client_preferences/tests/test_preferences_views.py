#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,arguments-differ

from hamcrest import is_
from hamcrest import none
from hamcrest import has_key
from hamcrest import has_entry
from hamcrest import has_entries
from hamcrest import assert_that
from hamcrest import is_not as does_not

from nti.app.testing.application_webtest import ApplicationTestLayer
from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS


class PrefApplicationTestLayer(ApplicationTestLayer):

    set_up_packages = (('test_preferences_views.zcml', 'nti.app.client_preferences.tests'),)

    @classmethod
    def setUp(cls):
        cls.setUpPackages()

    @classmethod
    def tearDown(cls):
        # We don't actually tear this down, but it shouldn't matter, everithing
        # is in our test namespace
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass


class TestPreferencesViews(ApplicationLayerTest):
    layer = PrefApplicationTestLayer

    @WithSharedApplicationMockDS(users=True, testapp=True)
    def test_traverse_to_my_root_prefs(self):
        res = self._fetch_user_url('/++preferences++')
        assert_that(res.json_body,
                    has_entries({'Class': 'Preference_Root',
                                 'href': '/dataserver2/users/sjohnson@nextthought.COM/++preferences++',
                                 'WebApp': has_entries({'Class': 'Preference_WebApp',
                                                        'MimeType': 'application/vnd.nextthought.preference.webapp',
                                                        'preferFlashVideo': False,
                                                        'useHighContrast': False}),
                                 'ChatPresence': has_entries({'Class': 'Preference_ChatPresence',
                                                              'MimeType': 'application/vnd.nextthought.preference.chatpresence',
                                                              'Away': has_entry('status', 'Away'),
                                                              'Available': has_entry('status', 'Available'),
                                                              'DND': has_entry('status', 'Do Not Disturb'),
                                                              'Active': is_(dict)}),
                                 'PushNotifications': has_entries({'Class': 'Preference_PushNotifications',
                                                                   'Email': {'Class': 'Preference_PushNotifications_Email',
                                                                             'MimeType': 'application/vnd.nextthought.preference.pushnotifications.email',
                                                                             'email_a_summary_of_interesting_changes': True,
                                                                             'notify_on_mention': True,
                                                                             'immediate_threadable_reply': False},
                                                                   'MimeType': 'application/vnd.nextthought.preference.pushnotifications',
                                                                   'send_me_push_notifications': True})}))
        # The hidden stuff is not present
        assert_that(res.json_body['ZMISettings'],
                    does_not(has_key('Hidden')))

        # But the read-only stuff is
        assert_that(res.json_body['ZMISettings'],
                    has_key('ReadOnly'))

    @WithSharedApplicationMockDS(users=True, testapp=True)
    def test_update_chat_active_prefs(self):
        href = '/dataserver2/users/sjohnson@nextthought.COM/++preferences++/ChatPresence/Active'
        self.testapp.put_json(href,
                              {'status': "This is my new status"})
        res = self._fetch_user_url('/++preferences++')
        assert_that(res.json_body,
                    has_entries('ChatPresence',
                                has_entry('Active',
                                          has_entry('status', 'This is my new status'))))

    @WithSharedApplicationMockDS(users=True, testapp=True)
    def test_cannot_update_read_only_prefs(self):
        href = '/dataserver2/users/sjohnson@nextthought.COM/++preferences++/ZMISettings/ReadOnly'
        self.testapp.get(href)
        self.testapp.put_json(href,
                              {'showZopeLogo': False},
                              status=422)

    @WithSharedApplicationMockDS(users=True, testapp=True)
    def test_traverse_to_my_zmi_prefs(self):
        res = self._fetch_user_url('/++preferences++/ZMISettings')
        assert_that(res.json_body,
                    has_entries('href', '/dataserver2/users/sjohnson@nextthought.COM/++preferences++/ZMISettings',
                                'email', none(),
                                'showZopeLogo', True,
                                'skin', 'Rotterdam',
                                'Class', 'Preference_ZMISettings',
                                'MimeType', 'application/vnd.nextthought.preference.zmisettings',
                                'Folder',  has_entries('Class', 'Preference_ZMISettings_Folder',
                                                       'MimeType', 'application/vnd.nextthought.preference.zmisettings.folder')))
        # And I can update them just like any external object
        self.testapp.put_json(res.json_body['href'], {'skin': 'Basic'})

        res = self._fetch_user_url('/++preferences++/ZMISettings')
        assert_that(res.json_body,
                    has_entries('skin', 'Basic'))
