# -*- coding: utf-8 -*-
#
# File: Location.py
#
# Copyright (c) 2008 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
# Generator: ArchGenXML Version 2.1
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

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='geometry',
        widget=StringField._properties['widget'](
            label="Geometry",
            description="""Geometry using GeoJSON shorthand representation such as "Point: (-105.0, 40.0)" for a point""",
            label_msgid='PleiadesEntity_label_geometry',
            description_msgid='PleiadesEntity_help_geometry',
            i18n_domain='PleiadesEntity',
        ),
    ),
    FloatField(
        name='accuracy',
        widget=FloatField._properties['widget'](
            label="Accuracy value",
            description="Accuracy (horizontal) of geometry coordinates in meters",
            label_msgid='PleiadesEntity_label_accuracy',
            description_msgid='PleiadesEntity_help_accuracy',
            i18n_domain='PleiadesEntity',
        ),
    ),
    StringField(
        name='explanation',
        widget=StringField._properties['widget'](
            label="Accuracy explanation",
            description="An explanation of the accuracy of the horizontal coordinate measurements and a description of the tests used.",
            label_msgid='PleiadesEntity_label_explanation',
            description_msgid='PleiadesEntity_help_explanation',
            i18n_domain='PleiadesEntity',
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Location_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
del Location_schema['title']
##/code-section after-schema

class Location(BaseFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.ILocation)

    meta_type = 'Location'
    _at_rename_after_creation = False

    schema = Location_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('get_title')
    def get_title(self):
        """Return a title string derived from the geometry type."""
        try:
            return "%s %s" % (self.getGeometry().split(':')[0], self.getId())
        except AttributeError:
            return 'Unidentified Location'

    security.declarePublic('Title')
    def Title(self):
        """
        """
        return self.get_title()

    security.declarePublic('getTimePeriods')
    def getTimePeriods(self):
        """
        """
        periods = []
        for ta in self.getFolderContents({'meta_type':['TemporalAttestation']}):
            periods.append(ta.getId)
        return periods


registerType(Location, PROJECTNAME)
# end of class Location

##code-section module-footer #fill in your manual code here
##/code-section module-footer



