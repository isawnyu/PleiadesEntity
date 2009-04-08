# -*- coding: utf-8 -*-
#
# File: FeatureContainer.py
#
# Copyright (c) 2009 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
# Generator: ArchGenXML Version 2.3
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


registerType(FeatureContainer, PROJECTNAME)
# end of class FeatureContainer

##code-section module-footer #fill in your manual code here
##/code-section module-footer



