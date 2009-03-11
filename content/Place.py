# -*- coding: utf-8 -*-
#
# File: Place.py
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

from Products.PleiadesEntity.config import *

# additional imports from tagged value 'import'
from Products.CMFCore import permissions

##code-section module-header #fill in your manual code here
from Products.CMFCore import permissions
import transaction
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATBackRef.backref import BackReferenceField, BackReferenceWidget
##/code-section module-header

schema = Schema((

    BackReferenceField(
        name='features',
        widget=BackReferenceWidget(
            visible={'view': 'visible', 'edit': 'invisible'},
            label="Place has feature part(s)",
            label_msgid='PleiadesEntity_label_features',
            i18n_domain='PleiadesEntity',
        ),
        multiValued=True,
        relationship="feature_place",
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
    ##/code-section class-header

    # Methods

    security.declareProtected(permissions.View, 'getFeatures')
    def getFeatures(self):
        """
        """
        for o in self.getBRefs('feature_place'):
            if interfaces.IFeature.providedBy(o):
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
            transaction.commit(1)
            self.setId(newid)

    security.declareProtected(permissions.View, 'getFeatureType')
    def getFeatureType(self):
        """
        """
        ftypes = []
        for f in self.getFeatures():
            ftype = f.getFeatureType()
            if ftype not in ftypes:
                ftypes.append(ftype)
        return ftypes


registerType(Place, PROJECTNAME)
# end of class Place

##code-section module-footer #fill in your manual code here
##/code-section module-footer



