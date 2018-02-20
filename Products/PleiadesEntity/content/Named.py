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
from Acquisition import aq_parent
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.PleiadesEntity.config import *

# additional imports from tagged value 'import'
from Products.CMFCore import permissions

##code-section module-header #fill in your manual code here
from AccessControl import getSecurityManager
from pleiades.vocabularies.vocabularies import get_vocabulary
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

    security.declareProtected(permissions.View, 'getSubConnections')
    def getSubConnections(self):
        """ List outbound Connection items contained inside this Named item.
        """
        checkPermission = getSecurityManager().checkPermission
        subcons = [
            o for o in self.values()
            if interfaces.IConnection.providedBy(o)
            and (checkPermission(permissions.View, o)
                 or checkPermission('Pleiades: View link to draft', o))
        ]
        print('getSubConnections got {} connections'.format(len(subcons)))
        return subcons

    security.declareProtected(permissions.View, 'getReverseConnections')
    def getReverseConnections(self):
        """ List inbound Connection items that are connected to this Named item.
        """
        checkPermission = getSecurityManager().checkPermission
        return [
            o for o in self.getBRefs('connection')
            if interfaces.IConnection.providedBy(o)
            and (checkPermission(permissions.View, o)
                 or checkPermission('Pleiades: View link to draft', o))
        ]

    security.declareProtected(permissions.View, 'getConnectedPlaces')
    def getConnectedPlaces(self):
        """ List Places connected via either inbound or outbound Connection objects.
        """
        found = set()
        places = []
        for connection in self.getSubConnections():
            place = connection.getConnection()
            if place.UID() not in found:
                places.append(place)
                found.add(place.UID())
        for connection in self.getReverseConnections():
            place = aq_parent(connection)
            if place.UID() not in found:
                places.append(place)
                found.add(place.UID())
        return places

    security.declareProtected(permissions.View, 'getConnectedPlaceUIDs')
    def getConnectedPlaceUIDs(self):
        """ List Places connected via either inbound or outbound Connection objects.
        """
        found = set()
        uids = []
        for connection in self.getSubConnections():
            refs = connection.getReferenceImpl('connection')
            if len(refs):
                uid = refs[0].targetUID
            if uid not in found:
                uids.append(uid)
                found.add(uid)
        for connection in self.getReverseConnections():
            place = aq_parent(connection)
            uid = place.UID()
            if uid not in found:
                uids.append(uid)
                found.add(uid)
        return uids

    security.declareProtected(permissions.View, 'getTimePeriods')
    def getTimePeriods(self):
        """
        """
        time_periods = get_vocabulary('time_periods')
        time_periods_list = [p['id'] for p in time_periods]
        def timeperiod_index(period):
            if period in time_periods_list:
                index = time_periods_list.index(period)
            else:
                index = -1
            return index
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
        return sorted([p for p in periods if p], key=timeperiod_index)

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



