#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generation 2 evolver, which migrates user preferences

.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from zope.component.hooks import site, setHooks

from zope.intid.interfaces import IIntIds

from zope.preference.interfaces import IUserPreferences

from zope.security.interfaces import IPrincipal
from zope.security.interfaces import IParticipation

from zope.security.management import newInteraction, endInteraction

from nti.contentfragments.interfaces import PlainTextContentFragment

from nti.dataserver.interfaces import IUser

generation = 2

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IParticipation)
class _Participation(object):

    __slots__ = ('interaction', 'principal')

    def __init__(self, principal):
        self.interaction = None
        self.principal = principal


def migrate_preferences(user):
    principal = IPrincipal(user)
    newInteraction(_Participation(principal))
    try:
        key = 'nti.dataserver.users.preferences.EntityPreferences'
        ep = getattr(user, '__annotations__', {}).get(key, None)
        if ep is None:
            return

        root_prefs = IUserPreferences(user)

        kalturaPreferFlash = ep.get('webapp_kalturaPreferFlash', None) \
                          or ep.get('kalturaPreferFlash')
        if kalturaPreferFlash is not None:
            webapp = root_prefs.WebApp
            webapp.preferFlashVideo = kalturaPreferFlash

        presence = ep.get('presence', {})
        current = presence.get('active')
        if current and current in presence:
            status = presence.get(current, {}).get('status')
            if status:
                root_prefs.ChatPresence.Active.status = PlainTextContentFragment(status)

        for name in ('Available', 'Away', 'DND'):
            status = presence.get(name.lower(), {}).get('status')
            pref_grp = getattr(root_prefs.ChatPresence, name)
            if status:
                pref_grp.status = PlainTextContentFragment(status)

        del user.__annotations__[key]
    finally:
        endInteraction()


def evolve(context):
    setHooks()
    ds_folder = context.connection.root()['nti.dataserver']
    lsm = ds_folder.getSiteManager()

    ds_intid = lsm.getUtility(provided=IIntIds)
    component.provideUtility(ds_intid, IIntIds)

    with site(ds_folder):
        assert component.getSiteManager() == ds_folder.getSiteManager(), \
               "Hooks not installed?"
        users = ds_folder['users']
        for user in users.values():
            if IUser.providedBy(user):
                migrate_preferences(user)

    component.getGlobalSiteManager().unregisterUtility(ds_intid, IIntIds)
