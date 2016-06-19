# -*- coding: utf-8 -*-
#
# File: Named.py
#
# Copyright (c) 2009 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
# Generator: ArchGenXML Version 2.4.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Sean Gillies <unknown>, Tom Elliott <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.PleiadesEntity.config import *

# additional imports from tagged value 'import'
from Products.CMFCore import permissions

##code-section module-header #fill in your manual code here
from Products.PleiadesEntity.time import TimePeriodCmp
from AccessControl import getSecurityManager
##/code-section module-header

schema = Schema((

    StringField(
        name='modernLocation',
        widget=StringField._properties['widget'](
            label="Modern location",
            description="Enter the name of a modern location or vicinity of the ancient place",
            label_msgid='PleiadesEntity_label_modernLocation',
            description_msgid='PleiadesEntity_help_modernLocation',
            i18n_domain='PleiadesEntity',
        ),
        description="The modern location or vicinity of the ancient place or feature",
    ),
    BooleanField(
        name='permanent',
        widget=BooleanField._properties['widget'](
            label="Permanent",
            description="Is the feature or place permanent, or existing across all time periods?",
            label_msgid='PleiadesEntity_label_permanent',
            description_msgid='PleiadesEntity_help_permanent',
            i18n_domain='PleiadesEntity',
        ),
        description="Permanence of the feature or place, regardless of name attestations",
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Named_schema = schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Named(BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.INamed)

    _at_rename_after_creation = True

    schema = Named_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declareProtected(permissions.View, 'get_title')
    def get_title(self):
        """Return a title string derived from contained ancient names.
        """
        try:
            names = self.getNames()
            if names:
                return '/'.join([n.Title() for n in names if n.Title()])
            else:
                return "Unnamed %s" % self.getFeatureType().capitalize()
        except AttributeError:
            return 'Unnamed Place'

    security.declareProtected(permissions.View, 'getNames')
    def getNames(self):
        """
        """
        checkPermission = getSecurityManager().checkPermission
        return [
            o for o in self.values()
            if interfaces.IName.providedBy(o)
            and (checkPermission('View', o)
                 or checkPermission('Pleiades: View link to draft', o))
        ]

    security.declareProtected(permissions.View, 'getLocations')
    def getLocations(self):
        """
        """
        checkPermission = getSecurityManager().checkPermission
        return [
            o for o in self.values()
            if interfaces.ILocation.providedBy(o)
            and (checkPermission(permissions.View, o)
                 or checkPermission('Pleiades: View link to draft', o))
        ]

    security.declareProtected(permissions.View, 'getTimePeriods')
    def getTimePeriods(self):
        """
        """
        periods = []
        for name in self.getNames():
            for a in name.getAttestations():
                if a['timePeriod'] not in periods:
                    periods.append(a['timePeriod'])
        if hasattr(self, 'getLocations'):
            for l6n in self.getLocations():
                for a in l6n.getAttestations():
                    if a['timePeriod'] not in periods:
                        periods.append(a['timePeriod'])
        if hasattr(self, 'getFeatures'):
            for f in self.getFeatures():
                for p in f.getTimePeriods():
                    if p not in periods:
                        periods.append(p)
        return sorted([p for p in periods if p], cmp=TimePeriodCmp(self))

    security.declareProtected(permissions.View, 'temporalRange')
    def temporalRange(self, period_ranges=None):
        """Nominal temporal range, not accounting for level of confidence"""
        years = []
        for child in (list(self.getNames()) + list(self.getLocations())):
            trange = child.temporalRange(period_ranges)
            if trange:
                years.extend(list(trange))
        if len(years) >= 2:
            return min(years), max(years)
        else:
            return None

# end of class Named

##code-section module-footer #fill in your manual code here
##/code-section module-footer



