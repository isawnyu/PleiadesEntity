# -*- coding: utf-8 -*-
#
# File: LocationContainer.py
#
# Copyright (c) 2008 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
# Generator: ArchGenXML Version 2.0
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

LocationContainer_schema = BaseBTreeFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class LocationContainer(BaseBTreeFolder, BrowserDefaultMixin):
    """Folder-ish container of Locations that also implements PCL
    s IFeatureStore.
    """
    security = ClassSecurityInfo()
    implements(interfaces.ILocationContainer)

    meta_type = 'LocationContainer'
    _at_rename_after_creation = True

    schema = LocationContainer_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declareProtected(permissions.AddPortalContent, 'invokeFactory')
    def invokeFactory(self, type_name, RESPONSE=None, **kw):
        """
        """
        pt = getToolByName(self, 'portal_types')
        if type_name != 'Location':
            raise ValueError, 'Disallowed subobject type: %s' % type_name
        id = self.generateId(prefix='')
        args = ('Location', self, id, RESPONSE)
        new_id = pt.constructContent(*args, **kw)
        if new_id is None or new_id == '':
            new_id = id
        return new_id


registerType(LocationContainer, PROJECTNAME)
# end of class LocationContainer

##code-section module-footer #fill in your manual code here
##/code-section module-footer



