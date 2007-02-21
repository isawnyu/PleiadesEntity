# -*- coding: utf-8 -*-
#
# File: PlaceContainer.py
#
# Copyright (c) 2007 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
# Generator: ArchGenXML Version 1.5.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Sean Gillies <unknown>, Tom Elliott <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
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

class PlaceContainer(BaseBTreeFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseBTreeFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Container for Places.'

    meta_type = 'PlaceContainer'
    portal_type = 'PlaceContainer'
    allowed_content_types = ['Place']
    filter_content_types = 1
    global_allow = 1
    #content_icon = 'PlaceContainer.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Container for Places."
    typeDescMsgId = 'description_edit_placecontainer'

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
        if id:
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



