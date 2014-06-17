#!/usr/bin/env python
"""
zope.generations installer for nti.app.client_preferences

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

generation = 2

from zope.generations.interfaces import IInstallableSchemaManager
from zope.generations.generations import SchemaManager as BaseSchemaManager

from zope import interface

@interface.implementer(IInstallableSchemaManager)
class SchemaManager(BaseSchemaManager):
	"A schema manager that we can register as a utility in ZCML."

	def __init__( self ):
		super(SchemaManager, self).__init__(
			generation=generation,
			minimum_generation=generation,
			package_name='nti.app.client_preferences.generations')

	def install( self, context ):
		# Nothing to do initially.
		# If there is something to do at a later generation,
		# the super class would default to calling
		# the 'evolve' method in this module.
		pass
