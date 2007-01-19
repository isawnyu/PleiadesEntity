# -*- coding: utf-8 -*-
#
# File: PlaceBucket.py
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

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlaceBucket_schema = BaseBTreeFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlaceBucket(BaseBTreeFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseBTreeFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'PlaceBucket'

    meta_type = 'PlaceBucket'
    portal_type = 'PlaceBucket'
    allowed_content_types = ['Place']
    filter_content_types = 1
    global_allow = 1
    #content_icon = 'PlaceBucket.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "PlaceBucket"
    typeDescMsgId = 'description_edit_placebucket'

    _at_rename_after_creation = True

    schema = PlaceBucket_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declareProtected(DEFAULT_ADD_CONTENT_PERMISSION, 'invokeFactory')
    def invokeFactory(self, type_name, id, RESPONSE=None, *args, **kw):
        """Override default.
        """
        pt = getToolByName(self, 'portal_types')
        new_id = None
        if type_name == 'Name':
            args = ('Place', self, self._v_nextid, RESPONSE)
            place_id = pt.constructContent(*args, **kw)
            self._v_nextid += 1
            place = getattr(self, place_id)
            args = ('Name', place, id, RESPONSE)
            name_id = pt.constructContent(*args, **kw)
            new_id = place_id
        else:
            raise NotImplemented, "Only Names may be added".

        return new_id


registerType(PlaceBucket, PROJECTNAME)
# end of class PlaceBucket

##code-section module-footer #fill in your manual code here
##/code-section module-footer



