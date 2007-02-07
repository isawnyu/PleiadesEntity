# ===========================================================================
# Copyright (c) 2007 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
#
# Generator: ArchGenXML Version 1.5.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# About Pleiades
# --------------
#
# Pleiades is an international research network and associated web portal and
# content management system devoted to the study of ancient geography. 
#
# See http://icon.stoa.org/trac/pleiades/wiki.
#
# Funding for the creation of this software was provided by a grant from the 
# U.S. National Endowment for the Humanities (http://www.neh.gov).
# ===========================================================================

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

LocationContainer_schema = BaseBTreeFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class LocationContainer(BaseBTreeFolder):
    """Folder-ish container of Locations that also implements PCL
    s IFeatureStore.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseBTreeFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Container for Locations'

    meta_type = 'LocationContainer'
    portal_type = 'LocationContainer'
    allowed_content_types = ['Location']
    filter_content_types = 1
    global_allow = 1
    #content_icon = 'LocationContainer.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Container for Locations"
    typeDescMsgId = 'description_edit_locationcontainer'

    _at_rename_after_creation = True

    schema = LocationContainer_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declareProtected(permissions.AddPortalContent, 'invokeFactory')
    def invokeFactory(self, type_name, RESPONSE=None):
        """
        """
        pt = getToolByName(self, 'portal_types')
        if type_name != 'Location':
            raise ValueError, 'Disallowed subobject type: %s' % type_name
        id = self._v_nextid
        args = ('Location', self, id, RESPONSE)
        new_id = pt.constructContent(*args)
        if new_id is None or new_id == '':
            new_id = id
        self._v_nextid += 1
        return new_id


registerType(LocationContainer, PROJECTNAME)
# end of class LocationContainer

##code-section module-footer #fill in your manual code here
##/code-section module-footer



