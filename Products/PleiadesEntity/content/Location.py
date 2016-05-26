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
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from decimal import Decimal
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.CMFCore import permissions
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.OrderableReferenceField import OrderableReferenceField
from Products.PleiadesEntity.content.Temporal import Temporal
from Products.PleiadesEntity.content.Work import Work
from Products.validation.interfaces.IValidator import IValidator
from shapely import wkt
from shapely.geometry import asShape
from shapely.geometry import mapping
from zope.interface import implements
#from zope.interface import implementer
from ..config import PROJECTNAME
import interfaces
import re
import simplejson


def decimalize(value):
    try:
        return [decimalize(inner) for inner in value]
    except:
        return Decimal("%s" % value)

##/code-section module-header

#@implementer(IValidator)
class CoordinatesValidator(object):

    implements(IValidator)

    name = 'coordinatesvalidator'

    def __call__(self, value, instance, *args, **kwargs):
        # ensure that the coordinates were entered according to specified forms

        value = value.strip()
        # Have we been given a latitude, longitude pair?
        m = re.match(r"(\-?\d+(\.\d+)?)\s*,*\s*(\-?\d+(\.\d+)?)", value)
        if m:
            return True
        if value == '{}':
            return "Coordinates format incorrect"
        
        # XXX add validation for GeoJSON here?
        return True

schema = atapi.Schema((

    atapi.StringField(
        name='featureType',
        widget=atapi.InAndOutWidget(
            label="Feature type",
            description="Feature type categories",
            label_msgid='PleiadesEntity_label_featureType',
            description_msgid='PleiadesEntity_help_featureType',
            i18n_domain='PleiadesEntity',
        ),
        description="Feature type categories",
        vocabulary=NamedVocabulary("""place-types"""),
        default=["unknown"],
        enforceVocabulary=1,
        multiValued=1,
    ),

    atapi.TextField(
        name='geometry',
        schemata="Coordinates",
        widget=atapi.TextAreaWidget(
            label="Geometry and coordinates (long, lat order)",
            description="""<p>Enter the coordinates of this location in one of 2 forms:<ol><li>Decimal latitude, longitude pair separated by whitespace or comma for point locations (example: <code>41.9, 12.5</code>)</li><li>GeoJSON (example: <code>{"type": "Point", "coordinates": [12.5,41.9]}</code>)</li></ol><p>Note that coordinate order in GeoJSON is longitude, latitude. Change focus to another form field and the map will update.</p>""",
            rows=4,
            label_msgid='PleiadesEntity_label_geometry',
            description_msgid='PleiadesEntity_help_geometry',
            i18n_domain='PleiadesEntity',
        ),
        default='',
        accessor='getGeometry',
        edit_accessor='getGeometryRaw',
        mutator='setGeometry',
        required=1,
        validators=(
            CoordinatesValidator(),)
    ),

    atapi.StringField(
        name='associationCertainty',
        widget=atapi.SelectionWidget(
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

    atapi.ReferenceField(
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

))

Location_schema = ATDocumentSchema.copy() + \
    schema.copy() + \
    getattr(Temporal, 'schema', atapi.Schema(())).copy() + \
    getattr(Work, 'schema', atapi.Schema(())).copy()
schema = Location_schema

off = {"edit": "invisible", "view": "invisible"}

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
    security = ClassSecurityInfo()

    implements(interfaces.ILocation)

    meta_type = 'Location'
    _at_rename_after_creation = True

    schema = Location_schema

    # Methods

    security.declareProtected(permissions.View, 'SearchableText')
    def SearchableText(self):
        text = super(Location, self).SearchableText().strip()
        return text + ' ' + self.rangesText()

    def _getGeometryRaw(self):
        return self.Schema()["geometry"].get(self)

    security.declareProtected(permissions.View, 'getGeometry')
    def getGeometry(self):
        """Return representation of geometry"""
        return self.getGeometryJSON(indent=2)

    security.declareProtected(permissions.View, 'getGeometryJSON')
    def getGeometryJSON(self, indent=None):
        """Return GeoJSON geometry"""
        raw = self._getGeometryRaw()
        if not raw:
            return 
        parts = raw.split(':')
        data = '{"type": "%s", "coordinates": %s}' % (
            parts[0].strip(), parts[1].strip())
        return simplejson.dumps(
            simplejson.loads(data, use_decimal=True),
            use_decimal=True,
            sort_keys=False,
            indent=indent
        )

    security.declareProtected(permissions.View, 'getGeometryWKT')
    def getGeometryWKT(self):
        """Return WKT representation of geometry"""
        parts = self._getGeometryRaw().split(':')
        j = '{"type": "%s", "coordinates": %s}' % (
            parts[0].strip(), parts[1].strip())
        d = simplejson.loads(j)
        return wkt.dumps(asShape(d))

    security.declarePublic('getGeometryRaw')
    def getGeometryRaw(self):
        return self.getGeometryJSON()

    security.declareProtected(permissions.ModifyPortalContent, 'setGeometry')
    def setGeometry(self, value):
        field = self.Schema()["geometry"]
        if not value:
            v = ""
        else:
            value = value.strip()
            # Have we been given a latitude, longitude pair?
            m = re.match(r"(\-?\d+(\.\d+)?)\s*,*\s*(\-?\d+(\.\d+)?)", value)
            if m:
                lat, lon = Decimal(m.group(1)), Decimal(m.group(3))
                v = "Point:[%s,%s]" % (lon, lat)
            # Determine whether we've been given GeoJSON or WKT
            else:
                # Correct common errors with input
                point_pat = re.compile("point", re.I)
                line_pat = re.compile("linestring", re.I)
                polygon_pat = re.compile("polygon", re.I)
                mpoint_pat = re.compile("multipoint", re.I)
                mline_pat = re.compile("multilinestring", re.I)
                mpolygon_pat = re.compile("multipolygon", re.I)
                type_pat = re.compile("type", re.I)
                coords_pat = re.compile("coordinates", re.I)
                value = re.sub(point_pat, "Point", value)
                value = re.sub(line_pat, "LineString", value)
                value = re.sub(polygon_pat, "Polygon", value)
                value = re.sub(mpoint_pat, "MultiPoint", value)
                value = re.sub(mline_pat, "MultiLineString", value)
                value = re.sub(mpolygon_pat, "MultiPolygon", value)
                value = re.sub(type_pat, "type", value)
                value = re.sub(coords_pat, "coordinates", value)
                text = value.strip()
                if text[0] == '{':
                    print "-1-"
                    # geojson
                    g = simplejson.loads(text, use_decimal=True)
                elif re.match(r'[a-zA-Z]+\s*\(', text):
                    print "-2-"
                    # WKT
                    g = mapping(wkt.loads(text))
                    g['coordinates'] = decimalize(g['coordinates'])
                else:
                    print "-3-"
                    # format X
                    parts = text.split(':')
                    coords = parts[1].replace('(', '[')
                    coords = coords.replace(')', ']')
                    j = '{"type": "%s", "coordinates": %s}' % (
                        parts[0].strip(), coords.strip())
                    g = simplejson.loads(j, use_decimal=True)

                v = "%s:%s" % (
                    g['type'], 
                    simplejson.dumps(g['coordinates'], use_decimal=True) )

        field.set(self, v)

atapi.registerType(Location, PROJECTNAME)
