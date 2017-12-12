#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,inherit-non-class

from hamcrest import none
from hamcrest import assert_that
from hamcrest import has_entries
from hamcrest import has_property

import zope.schema
import zope.interface

from zope.component import provideAdapter
from zope.component import provideUtility

from zope.interface.interface import taggedValue

from zope.preference import preference
from zope.preference.interfaces import IPreferenceGroup

from nti.externalization.internalization import update_from_external_object

# First, define a basic preference schema


class IBaseSettings(zope.interface.Interface):
    taggedValue('__external_preference_group__', 'write')


class IZMIUserSettings(IBaseSettings):
    """
    Basic User Preferences
    """
    # The root

    email = zope.schema.TextLine(
        title=u"E-mail Address",
        description=u"E-mail Address used to send notifications",
        required=False)

    skin = zope.schema.Choice(
        title=u"Skin",
        description=u"The skin that should be used for the ZMI.",
        values=[u'Rotterdam', u'ZopeTop', u'Basic'],
        default=u'Rotterdam')

    showZopeLogo = zope.schema.Bool(
        title=u"Show Zope Logo",
        description=u"Specifies whether Zope logo should be displayed "
        u"at the top of the screen.",
        default=True)


class IFolderSettings(IBaseSettings):
    """
    Basic User Preferences
    """
    # A child

    shownFields = zope.schema.Set(
        title=u"Shown Fields",
        description=u"Fields shown in the table.",
        value_type=zope.schema.Choice([u'name', u'size', u'creator']),
        default=set([u'name', u'size']))

    sortedBy = zope.schema.Choice(
        title=u"Sorted By",
        description=u"Data field to sort by.",
        values=[u'name', u'size', u'creator'],
        default=u'name')


class IReadOnlySettings(zope.interface.Interface):
    showZopeLogo = zope.schema.Bool(
        title=u"Show Zope Logo",
        description=u"Specifies whether Zope logo should be displayed "
        u"at the top of the screen.",
        default=True)
    taggedValue('__external_preference_group__', 'read')


class IHiddenSettings(zope.interface.Interface):
    showZopeLogo = zope.schema.Bool(
        title=u"Show Zope Logo",
        description=u"Specifies whether Zope logo should be displayed "
        u"at the top of the screen.",
        default=True)
    # No Tagged value


import zope.security.management

from zope.security.interfaces import NoInteraction
from zope.annotation.interfaces import IAnnotations
from zope.annotation.attribute import AttributeAnnotations

from nti.externalization.tests import externalizes

from nti.app.client_preferences.tests import PreferenceLayerTest


def _PrincipalAnnotationFactory(prin, unused_group):
    # The principal in the interaction must be annotatable
    # Making it implement IAttributeAnnotatable
    # seems like it should be enough (and it works for JAM)
    # but it doesn't work everywhere. So this is
    # an explicit factory.
    return AttributeAnnotations(prin)


class TestExternalizePreferences(PreferenceLayerTest):

    class Principal(object):
        id = u'zope.user'

    class Participation(object):
        interaction = None

        def __init__(self, p):
            self.principal = p

    settings = None

    def setUp(self):
        super(TestExternalizePreferences, self).setUp()
        self._create_prefs()
        provideAdapter(_PrincipalAnnotationFactory,
                       (self.Principal, IPreferenceGroup),
                       IAnnotations)

    def tearDown(self):
        zope.security.management.endInteraction()

    def _create_prefs(self):

        self.settings = preference.PreferenceGroup(
            "ZMISettings",
            schema=IZMIUserSettings,
            title=u"ZMI User Settings",
            description=u'')
        self.folder_settings = preference.PreferenceGroup(
            # Hierarchy matters! Must match utility names (happens
            # automatically from ZCML)
            'ZMISettings.Folder',
            schema=IFolderSettings,
            title=u"Folder Content View Settings")

    def test_no_interaction_fails(self):
        # Without an interaction, they cannot be read.
        # Without extra special work, prefs are always
        # for the current user
        try:
            assert_that(self.settings, externalizes())
            self.fail()
        except NoInteraction:
            pass

    def test_externalize_prefs(self):
        settings = self.settings

        participation = self.Participation(self.Principal())
        zope.security.management.newInteraction(participation)

        # Now it can work
        assert_that(settings, externalizes())

        # And when it does, all the defaults are taken into account
        assert_that(settings,
                    externalizes(has_entries('email', none(),
                                             'showZopeLogo', True,
                                             'skin', 'Rotterdam',
                                             'Class', 'Preference_ZMISettings',
                                             'MimeType', 'application/vnd.nextthought.preference.zmisettings')))

    def test_externalize_sub_prefs(self):
        # When we start with a root object,
        # and there are sub-objects in ZCA,
        # we get those as well
        participation = self.Participation(self.Principal())
        zope.security.management.newInteraction(participation)

        provideUtility(self.settings, IPreferenceGroup,
                       name=self.settings.__id__)
        provideUtility(self.folder_settings, IPreferenceGroup,
                       name=self.folder_settings.__id__)

        assert_that(self.settings,
                    externalizes(has_entries('Folder',
                                            has_entries('Class', 'Preference_ZMISettings_Folder',
                                                        'MimeType', 'application/vnd.nextthought.preference.zmisettings.folder'))))

    def test_update_prefs(self):
        participation = self.Participation(self.Principal())
        zope.security.management.newInteraction(participation)

        assert_that(self.settings, has_property('skin', 'Rotterdam'))
        update_from_external_object(self.settings, {'skin': 'Basic'})
        assert_that(self.settings, has_property('skin', 'Basic'))

    def test_update_sub_prefs(self):
        participation = self.Participation(self.Principal())
        zope.security.management.newInteraction(participation)

        provideUtility(self.settings, IPreferenceGroup,
                       name=self.settings.__id__)
        provideUtility(self.folder_settings, IPreferenceGroup,
                       name=self.folder_settings.__id__)

        assert_that(self.settings, has_property('skin', 'Rotterdam'))
        assert_that(self.folder_settings, has_property('sortedBy', 'name'))

        update_from_external_object(self.settings, 
                                    {'skin': u'Basic', u'Folder': {'sortedBy': u'creator'}})

        assert_that(self.settings, has_property('skin', 'Basic'))
        assert_that(self.folder_settings, has_property('sortedBy', 'creator'))

        # Be sure that it is actually in the annotations by
        # re-creating the objects
        self._create_prefs()
        assert_that(self.settings, has_property('skin', 'Basic'))
        assert_that(self.folder_settings, has_property('sortedBy', 'creator'))
