# -*- coding: utf-8 -*-
#
# File: PlaceContainer.py
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

PlaceContainer_schema = BaseBTreeFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlaceContainer(BaseBTreeFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IPlaceContainer)

    meta_type = 'PlaceContainer'
    _at_rename_after_creation = True

    schema = PlaceContainer_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declareProtected(permissions.AddPortalContent, 'invokeFactory')
    def invokeFactory(self, type_name, id=None, RESPONSE=None, **kw):
        """
        """
        pt = getToolByName(self, 'portal_types')
        myType = pt.getTypeInfo(self)
        if myType is not None:
            if not myType.allowType(type_name):
                raise ValueError, 'Disallowed subobject type: %s' % type_name

        # types other than Place
        if type_name != 'Place' and id is not None:
            args = (type_name, self, id, RESPONSE)
            new_id = pt.constructContent(*args, **kw)
            if new_id is None or new_id == '':
                new_id = id
            return new_id

        # Places are handled differently
        if id is not None:
            obid = str(id)
        else:
            # prevent ids in the reserved range
            obid = -1
            while int(obid) <= BA_ID_MAX:
                obid = self.generateId(prefix='')
        args = ('Place', self, obid, RESPONSE)
        new_id = pt.constructContent(*args, **kw)
        if new_id is None or new_id == '':
            new_id = obid
        return new_id


registerType(PlaceContainer, PROJECTNAME)
# end of class PlaceContainer

##code-section module-footer #fill in your manual code here
##/code-section module-footer



