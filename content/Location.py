# -*- coding: utf-8 -*-
#
# File: Location.py
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

    StringField(
        name='spatialGeometryType',
        widget=SelectionWidget(
            label="Geometry Type",
            description="Select geometry type",
            label_msgid='PleiadesEntity_label_spatialGeometryType',
            description_msgid='PleiadesEntity_help_spatialGeometryType',
            i18n_domain='PleiadesEntity',
        ),
        enforceVocabulary=1,
        vocabulary=['point', 'line', 'polygon', 'box']
    ),

    StringField(
        name='spatialCoordinates',
        widget=StringWidget(
            label="Spatial Coordinates",
            label_msgid='PleiadesEntity_label_spatialCoordinates',
            i18n_domain='PleiadesEntity',
        )
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Location_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Location(BaseFolder):
    """An ancient location or region
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Ancient Location'

    meta_type = 'Location'
    portal_type = 'Location'
    allowed_content_types = ['Reference', 'TemporalAttestation', 'SecondaryReference', 'PrimaryReference']
    filter_content_types = 1
    global_allow = 0
    content_icon = 'link_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Ancient Location"
    typeDescMsgId = 'description_edit_location'

    _at_rename_after_creation = True

    schema = Location_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(Location, PROJECTNAME)
# end of class Location

##code-section module-footer #fill in your manual code here
##/code-section module-footer



