# -*- coding: utf-8 -*-
#
# File: Place.py
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
from AccessControl import getSecurityManager
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from Products.Archetypes import atapi
from Products.ATBackRef.backref import BackReferenceField, BackReferenceWidget
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.CMFCore import permissions
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.PleiadesEntity.content.Named import Named
from Products.PleiadesEntity.content.Work import Work
from zope.interface import implements
from ..AppConfig import BA_ID_MAX
from ..config import PROJECTNAME
import interfaces
import transaction


VIEW_MAP = {
    'text/html': 'base_view',
    'application/xhtml+xml': 'base_view',
    'application/json': u'json',
    'application/javascript': u'json',
    'application/x-javascript': u'json',
    'text/javascript': u'json',
    'aplication/ld+json': u'json',
    'application/vnd.geo+json': u'json',
    'application/rdf+xml': u'rdf',
    'text/turtle': 'turtle',
    'application/x-turtle': u'turtle',
    'application/turtle': u'turtle',
    'application/vnd.google-earth.kml+xml': u'kml',
    'application/vnd.google-earth.kmz': u'kml',
}

schema = atapi.Schema((

    atapi.LinesField(
        name='placeType',
        widget=atapi.InAndOutWidget(
            label="Place type",
            description="Select type of place",
            label_msgid='PleiadesEntity_label_placeType',
            description_msgid='PleiadesEntity_help_placeType',
            i18n_domain='PleiadesEntity',
        ),
        description="Type of place",
        vocabulary_factory='pleiades.vocabularies.place_types',
        default=["unknown"],
        enforceVocabulary=1,
        multiValued=1,
        accessor='getFeatureType',
        edit_accessor='getPlaceTypeRaw'
    ),

    atapi.ReferenceField(
        name='connections',
        widget=ReferenceBrowserWidget(
            label="Makes a connection with",
            description="Establishes a connection to another place.",
            startup_directory="/places",
            allow_browse=0,
            allow_search=1,
            base_query={'portal_type': ['Place']},
            search_index='SearchableText',
            label_msgid='PleiadesEntity_label_connections',
            i18n_domain='PleiadesEntity',
            hide_inaccessible=True,
        ),
        multiValued=True,
        relationship='connectsWith',
        allowed_types="('Place',)",
    ),

    BackReferenceField(
        name='connections_from',
        widget=BackReferenceWidget(
            visible="{'view': 'visible', 'edit': 'invisible'}",
            label="Has a connection with",
            macro="betterbackrefwidget",
            label_msgid='PleiadesEntity_label_connectsWith',
            i18n_domain='PleiadesEntity',
            hide_inaccessible=True,
        ),
        multiValued=True,
        relationship="connectsWith",
    ),

))


Place_schema = ATDocumentSchema.copy() + \
    schema.copy() + \
    getattr(Named, 'schema', atapi.Schema(())).copy() + \
    getattr(Work, 'schema', atapi.Schema(())).copy()
schema = Place_schema

off = {"edit": "invisible", "view": "invisible"}

schema["effectiveDate"].widget.visible = off
schema["expirationDate"].widget.visible = off
schema["allowDiscussion"].widget.visible = off
schema["excludeFromNav"].widget.visible = off
schema["text"].widget.label = 'Details'
schema["presentation"].widget.visible = off
schema["tableContents"].widget.visible = off
schema["text"].schemata = "Details"

schemata.finalizeATCTSchema(
    Place_schema,
    folderish=True,
    moveDiscussion=False
)


class Place(atapi.BaseFolder, ATDocumentBase, Named, Work, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IPlace)

    meta_type = 'Place'
    _at_rename_after_creation = True

    schema = Place_schema
    schema["presentation"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["tableContents"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["text"].widget.label = 'Details'
    schema["permanent"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["modernLocation"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema.moveField('placeType', after='description')
    schema.moveField('text', pos='bottom')

    # Methods

    security.declareProtected(permissions.View, 'getFeatures')
    def getFeatures(self):
        """
        """
        sm = getSecurityManager()
        for o in self.getBRefs('feature_place'):
            if interfaces.IFeature.providedBy(o) and sm.checkPermission(permissions.View, o):
                yield o

    security.declareProtected(permissions.AddPortalContent, '_renameAfterCreation')
    def _renameAfterCreation(self, check_auto_id=False):
        try:
            oldint = int(self.getId())
            if oldint <= BA_ID_MAX:
                oldid = str(oldint)
            else:
                oldid = None
        except ValueError:
            oldid = None
        if oldid is None:
            parent = self.aq_inner.aq_parent
            newid = -1
            while int(newid) <= BA_ID_MAX:
                newid = parent.generateId(prefix='')
            transaction.commit()
            self.setId(newid)

    security.declareProtected(permissions.View, 'getPlaceTypeRaw')
    def getPlaceTypeRaw(self):
        """ """
        return self.Schema()["placeType"].get(self)

    security.declareProtected(permissions.View, 'getPlaceType')
    def getPlaceType(self):
        """ """
        return [t for t in self.getPlaceTypeRaw() if bool(t)]

    security.declareProtected(permissions.View, 'getFeatureType')
    def getFeatureType(self):
        """Get list of feature types for the place, digging into backref'd
        features if no types are explicitly set on the place.
        """
        ftypes = self.getPlaceType()
        for f in list(self.getLocations()) + list(self.getFeatures()):
            ftypes.extend([t for t in f.getFeatureType() if bool(t)])
        ftypes = set(ftypes)
        if len(ftypes) > 1 and 'unknown' in ftypes:
            ftypes.remove('unknown')
        return list(ftypes)

    security.declarePublic('SearchableText')
    def SearchableText(self):
        text = super(Place, self).SearchableText().strip()
        return "%s %s %s" % (
            text,
            self.getModernLocation(),
            self.rangesText(),
        )

    security.declareProtected(permissions.View, 'getLayout')
    def getLayout(self, **kw):
        """Check ACCEPT header for known formats/views and render."""
        request = getattr(self, 'REQUEST', None)
        default = super(Place, self).getLayout(**kw)
        if request is None:
            return default
        res = request.response
        res.setHeader('Vary', 'Accept')
        accept = request.environ.get('HTTP_ACCEPT', '').split(',')
        user_preferences = []
        for value in accept:
            parts = value.split(";")
            weight = 1.0
            if len(parts) == 2:
                try:
                    weight = float(parts[1].split("=")[1])
                except:
                    weight = 0.3
            user_preferences.append((weight, parts[0].strip()))
        user_preferences.sort(reverse=True)

        for weight, preferred in user_preferences:
            if preferred in VIEW_MAP:
                return VIEW_MAP[preferred]
            if 'html' in preferred or '*' in preferred:
                return 'base_view'

        request.form['pid'] = self.getId()
        return "conneg_406_message"

atapi.registerType(Place, PROJECTNAME)
