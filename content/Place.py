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
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces
from Products.PleiadesEntity.content.Named import Named
from Products.PleiadesEntity.content.Work import Work
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.OrderableReferenceField import OrderableReferenceField, OrderableReferenceWidget
from Products.PleiadesEntity.config import *

# additional imports from tagged value 'import'
from Products.CMFCore import permissions
from Products.ATBackRef.backref import BackReferenceField, BackReferenceWidget

##code-section module-header #fill in your manual code here
from Products.CMFCore import permissions
import transaction
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATBackRef.backref import BackReferenceField, BackReferenceWidget
from AccessControl import getSecurityManager
##/code-section module-header

schema = Schema((

    StringField(
        name='placeType',
        widget=InAndOutWidget(
            label="Place type",
            description="Select type of place",
            label_msgid='PleiadesEntity_label_placeType',
            description_msgid='PleiadesEntity_help_placeType',
            i18n_domain='PleiadesEntity',
        ),
        description="Type of place",
        vocabulary=NamedVocabulary("""place-types"""),
        default=["unknown"],
        enforceVocabulary=1,
        multiValued=1,
    ),

    OrderableReferenceField(
        name='parts',
        widget=ReferenceBrowserWidget(
            label="Has part(s)",
            description="Order is important for graph-like places: roads, itineraries, etc",
            startup_directory="/places",
            label_msgid='PleiadesEntity_label_places',
            i18n_domain='PleiadesEntity',
        ),
        multiValued=True,
        relationship='hasPart',
        allowed_types="('Place',)",
        allow_browse="True",
    ),

    BackReferenceField(
        name='places',
        widget=BackReferenceWidget(
            visible="{'view': 'visible', 'edit': 'invisible'}",
            label="Is a part of",
            macro="betterbackrefwidget",
            label_msgid='PleiadesEntity_label_features',
            i18n_domain='PleiadesEntity',
        ),
        multiValued=True,
        relationship="hasPart",
    ),

    ReferenceField(
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
        ),
        multiValued=True,
        relationship='connectsWith',
        allowed_types="('Place',)",
    ),

    BackReferenceField(
        name='connectsWith',
        widget=BackReferenceWidget(
            visible="{'view': 'visible', 'edit': 'invisible'}",
            label="Has a connection with",
            macro="betterbackrefwidget",
            label_msgid='PleiadesEntity_label_connectsWith',
            i18n_domain='PleiadesEntity',
        ),
        multiValued=True,
        relationship="connectsWith",
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Place_schema = BaseFolderSchema.copy() + \
    getattr(Named, 'schema', Schema(())).copy() + \
    getattr(Work, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
Place_schema = ATDocumentSchema.copy() + \
    schema.copy() + \
    getattr(Named, 'schema', Schema(())).copy() + \
    getattr(Work, 'schema', Schema(())).copy()
##/code-section after-schema

class Place(BaseFolder, ATDocumentBase, Named, Work, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IPlace)

    meta_type = 'Place'
    _at_rename_after_creation = True

    schema = Place_schema

    ##code-section class-header #fill in your manual code here
    schema["presentation"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["tableContents"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["text"].widget.label = 'Details'
    schema["parts"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["places"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["permanent"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["modernLocation"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema.moveField('placeType', pos='top')
    ##/code-section class-header

    # Methods

    security.declareProtected(permissions.View, 'getFeatures')
    def getFeatures(self):
        """
        """
        sm = getSecurityManager()
        for o in self.getBRefs('feature_place'):
            if interfaces.IFeature.providedBy(o) and sm.checkPermission(permissions.View, o):
                yield o

    security.declareProtected(permissions.View, 'getParts')
    def getParts(self):
        """
        """
        sm = getSecurityManager()
        for o in self.getRefs('hasPart'):
            if interfaces.IPlace.providedBy(o) and sm.checkPermission(permissions.View, o):
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

    security.declareProtected(permissions.View, 'getFeatureType')
    def getFeatureType(self):
        """Get list of feature types for the place, digging into backref'd
        features if no types are explicitly set on the place.
        """
        ftypes = [t for t in self.getPlaceType() if bool(t)]
        if not ftypes or ftypes == ['unknown']:
            for f in self.getFeatures():
                candidates = [t for t in f.getFeatureType() if bool(t)]
                for t in candidates:
                    if t not in ftypes:
                        ftypes.append(t)
        if len(ftypes) > 1 and 'unknown' in ftypes:
            ftypes.remove('unknown')
        return ftypes

    security.declarePublic('SearchableText')
    def SearchableText(self):
        text = super(Place, self).SearchableText().strip()
        return "%s %s %s" % ( text
                            , self.getModernLocation()
                            , self.rangesText()
                            )

registerType(Place, PROJECTNAME)
# end of class Place

##code-section module-footer #fill in your manual code here
##/code-section module-footer



