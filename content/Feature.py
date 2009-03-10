# -*- coding: utf-8 -*-
#
# File: Feature.py
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
from Products.PleiadesEntity.content.Named import Named
from Products.PleiadesEntity.content.Work import Work
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.PleiadesEntity.config import *

# additional imports from tagged value 'import'
from Products.CMFCore import permissions

##code-section module-header #fill in your manual code here
import transaction
##/code-section module-header

schema = Schema((

    StringField(
        name='featureType',
        widget=SelectionWidget(
            label="Feature type",
            description="Select type of feature",
            label_msgid='PleiadesEntity_label_featureType',
            description_msgid='PleiadesEntity_help_featureType',
            i18n_domain='PleiadesEntity',
        ),
        description="Type of feature",
        vocabulary=NamedVocabulary("""place-types"""),
        default="unknown",
        enforceVocabulary=1,
    ),
    BooleanField(
        name='permanent',
        widget=BooleanField._properties['widget'](
            label="Permanent",
            description="Is the feature permanent, or existing across all time periods?",
            label_msgid='PleiadesEntity_label_permanent',
            description_msgid='PleiadesEntity_help_permanent',
            i18n_domain='PleiadesEntity',
        ),
        description="Permanence of the feature, regardless of name attestations",
    ),
    ReferenceField(
        name='places',
        widget=ReferenceBrowserWidget(
            label="Feature is a part of place(s)",
            startup_directory="/places",
            label_msgid='PleiadesEntity_label_places',
            i18n_domain='PleiadesEntity',
        ),
        multiValued=1,
        relationship="feature_place",
        allowed_types=('Place',),
        allow_browse=1,
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
Feature_schema = BaseFolderSchema.copy() + \
    schema.copy() + \
    getattr(Named, 'schema', Schema(())).copy() + \
    getattr(Work, 'schema', Schema(())).copy()
##/code-section after-schema

class Feature(BaseFolder, Named, Work):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IFeature)

    meta_type = 'Feature'
    _at_rename_after_creation = True

    schema = Feature_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declareProtected(permissions.View, 'getLocations')
    def getLocations(self):
        """
        """
        return [o for o in self.values() if interfaces.ILocation.providedBy(o)]

    security.declareProtected(permissions.AddPortalContent, '_renameAfterCreation')
    def _renameAfterCreation(self, check_auto_id=False):
        parent = self.aq_inner.aq_parent
        newid = parent.generateId(prefix='')
        # Can't rename without a subtransaction commit when using
        # portal_factory!
        transaction.commit(1)
        self.setId(newid)


registerType(Feature, PROJECTNAME)
# end of class Feature

##code-section module-footer #fill in your manual code here
##/code-section module-footer



