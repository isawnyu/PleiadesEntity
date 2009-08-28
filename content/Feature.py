# -*- coding: utf-8 -*-
#
# File: Feature.py
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

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.PleiadesEntity.config import *

# additional imports from tagged value 'import'
from Products.CMFCore import permissions
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

##code-section module-header #fill in your manual code here
import transaction
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from AccessControl import getSecurityManager
##/code-section module-header

schema = Schema((

    StringField(
        name='featureType',
        widget=InAndOutWidget(
            label="Feature type",
            description="Select type of feature",
            label_msgid='PleiadesEntity_label_featureType',
            description_msgid='PleiadesEntity_help_featureType',
            i18n_domain='PleiadesEntity',
        ),
        description="Type of feature",
        vocabulary=NamedVocabulary("""place-types"""),
        default=["unknown"],
        enforceVocabulary=1,
        multiValued=1,
    ),
    ReferenceField(
        name='places',
        widget=ReferenceBrowserWidget(
            label="Feature is a part of place(s)",
            startup_directory="/places",
            label_msgid='PleiadesEntity_label_places',
            i18n_domain='PleiadesEntity',
        ),
        multiValued=True,
        relationship='feature_place',
        allowed_types="('Place',)",
        allow_browse="True",
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Feature_schema = BaseFolderSchema.copy() + \
    getattr(Named, 'schema', Schema(())).copy() + \
    getattr(Work, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
Feature_schema = ATDocumentSchema.copy() + \
    schema.copy() + \
    getattr(Named, 'schema', Schema(())).copy() + \
    getattr(Work, 'schema', Schema(())).copy()
##/code-section after-schema

class Feature(BaseFolder, ATDocumentBase, Named, Work, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IFeature)

    meta_type = 'Feature'
    _at_rename_after_creation = True

    schema = Feature_schema

    ##code-section class-header #fill in your manual code here
    schema["modernLocation"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["presentation"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["tableContents"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["text"].widget.label = 'Details'
    ##/code-section class-header

    # Methods

    security.declareProtected(permissions.View, 'getLocations')
    def getLocations(self):
        """
        """
        sm = getSecurityManager()
        return [o for o in self.values() if interfaces.ILocation.providedBy(o) and sm.checkPermission(permissions.View, o)]

    security.declareProtected(permissions.AddPortalContent, '_renameAfterCreation')
    def _renameAfterCreation(self, check_auto_id=False):
        parent = self.aq_inner.aq_parent
        newid = parent.generateId(prefix='')
        # Can't rename without a subtransaction commit when using
        # portal_factory!
        transaction.commit(1)
        self.setId(newid)

    security.declarePublic('SearchableText')
    def SearchableText(self):
        text = super(Feature, self).SearchableText().strip()
        return text + ' ' + self.rangesText()


registerType(Feature, PROJECTNAME)
# end of class Feature

##code-section module-footer #fill in your manual code here
##/code-section module-footer



