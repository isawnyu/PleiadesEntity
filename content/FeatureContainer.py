# -*- coding: utf-8 -*-
#
# File: FeatureContainer.py
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

# additional imports from tagged value 'import'
from Products.CMFCore import permissions

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((


),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

FeatureContainer_schema = BaseBTreeFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class FeatureContainer(BaseBTreeFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IFeatureContainer)

    meta_type = 'FeatureContainer'
    _at_rename_after_creation = True

    schema = FeatureContainer_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('invokeFactory')
    def invokeFactory(self, type_name, id=None, RESPONSE=None, **kw):
        """
        """
        pt = getToolByName(self, 'portal_types')
        if type_name == 'Feature' or id is None:
            oid = self.generateId(prefix='')
        else:
            oid = id
        args = (type_name, self, oid, RESPONSE)
        new_id = pt.constructContent(*args, **kw)
        if new_id is None or new_id == '':
            new_id = oid
        return new_id


registerType(FeatureContainer, PROJECTNAME)
# end of class FeatureContainer

##code-section module-footer #fill in your manual code here
##/code-section module-footer



