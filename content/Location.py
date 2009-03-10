# -*- coding: utf-8 -*-
#
# File: Location.py
#
# Copyright (c) 2009 by Ancient World Mapping Center, University of North
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
from Products.PleiadesEntity.content.Work import Work
from Products.PleiadesEntity.content.Temporal import Temporal
from Products.PleiadesEntity.content.Work import Work
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget
from Products.PleiadesEntity.config import *

# additional imports from tagged value 'import'
from Products.CMFCore import permissions
##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='geometry',
        widget=StringField._properties['widget'](
            label="Geometry",
            description="""Enter geometry using GeoJSON shorthand representation such as "Point: (-105.0, 40.0)" for a point""",
            label_msgid='PleiadesEntity_label_geometry',
            description_msgid='PleiadesEntity_help_geometry',
            i18n_domain='PleiadesEntity',
        ),
    ),
    StringField(
        name='description',
        widget=StringField._properties['widget'](
            label="Alternate description",
            description="""Enter alternate description of location (for example: "10 km N of Athens")""",
            label_msgid='PleiadesEntity_label_description',
            description_msgid='PleiadesEntity_help_description',
            i18n_domain='PleiadesEntity',
        ),
        description="Location as a text string suitable for geocoding",
    ),
    ReferenceField(
        name='accuracy',
        widget=ReferenceBrowserWidget(
            startup_directory="/features/metadata",
            label="Accuracy assessment",
            label_msgid='PleiadesEntity_label_accuracy',
            i18n_domain='PleiadesEntity',
        ),
        multiValued=0,
        relationship="location_accuracy",
        allowed_types=('PositionalAccuracy',),
        allow_browse=1,
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Location_schema = BaseSchema.copy() + \
    getattr(Work, 'schema', Schema(())).copy() + \
    getattr(Temporal, 'schema', Schema(())).copy() + \
    getattr(Work, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
Location_schema = BaseSchema.copy() + \
    schema.copy() + \
    getattr(Temporal, 'schema', Schema(())).copy() + \
    getattr(Work, 'schema', Schema(())).copy()
##/code-section after-schema

class Location(BaseContent, Work, Temporal, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.ILocation)

    meta_type = 'Location'
    _at_rename_after_creation = True

    schema = Location_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(Location, PROJECTNAME)
# end of class Location

##code-section module-footer #fill in your manual code here
##/code-section module-footer



