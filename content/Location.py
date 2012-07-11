# -*- coding: utf-8 -*-
#
# File: Location.py
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
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.CompoundField.ArrayField import ArrayField
from Products.CompoundField.ArrayWidget import ArrayWidget
from Products.CompoundField.EnhancedArrayWidget import EnhancedArrayWidget
from Products.CompoundField.EnhancedArrayWidget import EnhancedArrayWidget
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.OrderableReferenceField import OrderableReferenceField, OrderableReferenceWidget
from Products.PleiadesEntity.config import *
from Products.PleiadesEntity.content.Work import Work
from Products.PleiadesEntity.content.Temporal import Temporal

# additional imports from tagged value 'import'
from Products.CMFCore import permissions
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
##code-section module-header #fill in your manual code here
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATContentTypes.content import schemata

import re
from shapely.geometry import asShape
from shapely import wkt
import simplejson
##/code-section module-header

schema = Schema((

    TextField(
        name='geometry',
        schemata="Coordinates",
        widget=TextAreaWidget(
            label="Geometry",
            description="""Enter geometry using GeoJSON shorthand representation with longitude (decimal degrees east of the Greenwich Meridian), latitude (decimal degrees north of the Equator) coordinate ordering, such as "Point:[-105.0, 40.0]" for a point or "Polygon:[[[28.72188, 37.70815], [28.72194, 37.70741], [28.72241, 37.70744], [28.72233, 37.70819], [28.72188, 37.70815]]]" for a region. Values in WKT or full GeoJSON format, with the same longitude/latitude ordering, are also acceptable.""",
            rows=10,
            label_msgid='PleiadesEntity_label_geometry',
            description_msgid='PleiadesEntity_help_geometry',
            i18n_domain='PleiadesEntity',
        ),
        default='',
        accessor='getGeometry',
        edit_accessor='getGeometryRaw',
        mutator='setGeometry',
    ),

    StringField(
        name='associationCertainty',
        widget=SelectionWidget(
            label="Association Certainty",
            description="Select level of certainty in association between location and place",
            label_msgid='PleiadesEntity_label_associationCertainty',
            description_msgid='PleiadesEntity_help_associationCertainty',
            i18n_domain='PleiadesEntity',
        ),
        description="Level of certainty in association between location and place",
        vocabulary=NamedVocabulary("""association-certainty"""),
        default="certain",
        enforceVocabulary=1,
    ),

    ReferenceField(
        name='accuracy',
        schemata="Coordinates",
        widget=ReferenceBrowserWidget(
            startup_directory="/features/metadata",
            label="Positional Accuracy Assessment",
            description="Select document describing the postional accuracy of this location",
            label_msgid='PleiadesEntity_label_accuracy',
            i18n_domain='PleiadesEntity',
        ),
        multiValued=False,
        relationship='location_accuracy',
        allow_browse="True",
    ),

    OrderableReferenceField(
        name='nodes',
        widget=ReferenceBrowserWidget(
            startup_directory="/places",
            label="Connects",
            description=u'Select places or locations to add in order',
            label_msgid='PleiadesEntity_label_nodes',
            i18n_domain='PleiadesEntity',
        ),
        description="Feature node in a network location",
        multiValued=True,
        relationship='location_node',
        allowed_types=('Place', 'Location'),
        allow_browse="True",
    ),


),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

#Location_schema = BaseSchema.copy() + \
#    getattr(Temporal, 'schema', Schema(())).copy() + \
#    getattr(Work, 'schema', Schema(())).copy() + \
#    schema.copy()

##code-section after-schema #fill in your manual code here
Location_schema = ATDocumentSchema.copy() + \
    schema.copy() + \
    getattr(Temporal, 'schema', Schema(())).copy() + \
    getattr(Work, 'schema', Schema(())).copy()
##/code-section after-schema

off = {"edit": "invisible", "view": "invisible"}

schema = Location_schema

schema["effectiveDate"].widget.visible = off
schema["expirationDate"].widget.visible = off
schema["allowDiscussion"].widget.visible = off
schema["excludeFromNav"].widget.visible = off
schema["presentation"].widget.visible = off
schema["tableContents"].widget.visible = off
schema["nodes"].widget.visible = off
schema["text"].widget.label = 'Details'
schema["text"].schemata = "Details"
schema.moveField('text', pos='bottom')

schemata.finalizeATCTSchema(
    Location_schema,
    folderish=False,
    moveDiscussion=False
)

class Location(ATDocumentBase, Work, Temporal, BrowserDefaultMixin):
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

    security.declareProtected(permissions.View, 'SearchableText')
    def SearchableText(self):
        text = super(Location, self).SearchableText().strip()
        return text + ' ' + self.rangesText()

    security.declareProtected(permissions.View, 'getGeometry')
    def getGeometry(self):
        return self.getGeometryRaw()

    security.declareProtected(permissions.View, 'getGeometryJSON')
    def getGeometryJSON(self):
        parts = self.getGeometryRaw().split(':')
        return '{"type": "%s", "coordinates": %s}' % (
            parts[0].strip(), parts[1].strip())

    security.declareProtected(permissions.View, 'getGeometryWKT')
    def getGeometryWKT(self):
        parts = self.getGeometryRaw().split(':')
        j = '{"type": "%s", "coordinates": %s}' % (
            parts[0].strip(), parts[1].strip())
        d = simplejson.loads(j)
        return wkt.dumps(asShape(d))

    security.declarePublic('getGeometryRaw')
    def getGeometryRaw(self):
        return self.Schema()["geometry"].get(self)

    security.declareProtected(permissions.ModifyPortalContent, 'setGeometry')
    def setGeometry(self, value):
        field = self.Schema()["geometry"]
        if not value:
            v = ''
        else:
            text = value.strip()
            if text[0] == '{':
                # geojson
                g = simplejson.loads(text)
            elif re.match(r'[a-zA-Z]+\s*\(', text):
                # WKT
                gi = wkt.loads(text).__geo_interface__
                g = simplejson.loads(simplejson.dumps(gi))
            else:
                # format X
                parts = text.split(':')
                coords = parts[1].replace('(', '[')
                coords = coords.replace(')', ']')
                j = '{"type": "%s", "coordinates": %s}' % (
                    parts[0].strip(), coords.strip())
                g = simplejson.loads(j)
            v = "%s:%s" % (g['type'], g['coordinates'])
        field.set(self, v)

registerType(Location, PROJECTNAME)
# end of class Location

##code-section module-footer #fill in your manual code here
##/code-section module-footer



