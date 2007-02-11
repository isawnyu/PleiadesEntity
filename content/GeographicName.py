# -*- coding: utf-8 -*-
#
# File: GeographicName.py
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
from Products.PleiadesEntity.content.Name import Name
from Products.PleiadesEntity.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

GeographicName_schema = BaseFolderSchema.copy() + \
    getattr(Name, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class GeographicName(Name, BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(Name,'__implements__',()),) + (getattr(BaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Ancient Geographic Name'

    meta_type = 'GeographicName'
    portal_type = 'GeographicName'
    allowed_content_types = [] + list(getattr(Name, 'allowed_content_types', []))
    filter_content_types = 1
    global_allow = 0
    #content_icon = 'GeographicName.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Any name used in antiquity to designate a site or locale, but not a people or tribe"
    typeDescMsgId = 'description_edit_geographicname'

    _at_rename_after_creation = True

    schema = GeographicName_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(GeographicName, PROJECTNAME)
# end of class GeographicName

##code-section module-footer #fill in your manual code here
##/code-section module-footer



