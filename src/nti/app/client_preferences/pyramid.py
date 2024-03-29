#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Support for viewing and updating preferences.

.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from pyramid.view import view_config

from zope.preference.interfaces import IPreferenceGroup

from nti.app.base.abstract_views import AbstractAuthenticatedView

from nti.app.externalization.view_mixins import ModeledContentUploadRequestUtilsMixin

from nti.dataserver import authorization as nauth

logger = __import__('logging').getLogger(__name__)


@view_config(route_name='objects.generic.traversal',
             request_method='GET',
             renderer='rest',
             context=IPreferenceGroup,
             permission=nauth.ACT_READ)
def PreferencesGetView(request):
    # This checks adaptation to annotations
    # and the security interaction all at the same time
    # Because we load the ++preference++ traversal namespace,
    # this is available at /path/to/principal/++preference++
    # (and sub-paths, nice! for automatic fetch-in-part)
    # We should supply etag and/or last modified for this
    # (does the default etag kick in?)
    return request.context


@view_config(route_name='objects.generic.traversal',
             request_method='PUT',
             renderer='rest',
             context=IPreferenceGroup,
             permission=nauth.ACT_UPDATE)
class PreferencesPutView(AbstractAuthenticatedView,
                         ModeledContentUploadRequestUtilsMixin):
    # Although this is the UPDATE permission,
    # the prefs being updated are always those of the current user
    # implicitly, regardless of traversal path. We could add
    # an ACLProvider (and hook into the zope checker machinery?)
    # but that would be primarily for aesthetics
    def __call__(self):
        externalValue = self.readInput()
        return self.updateContentObject(self.request.context, externalValue, notify=False)
