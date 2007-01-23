# -*- coding: utf-8 -*-
#
# File: Place.py
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
        name='placeType',
        widget=StringWidget(
            label="Place Type",
            label_msgid='PleiadesEntity_label_placeType',
            i18n_domain='PleiadesEntity',
        )
    ),

    StringField(
        name='modernLocation',
        widget=StringWidget(
            label="Modern Location",
            label_msgid='PleiadesEntity_label_modernLocation',
            i18n_domain='PleiadesEntity',
        )
    ),

    ReferenceField(
        name='locations',
        widget=ReferenceWidget(
            label='Locations',
            label_msgid='PleiadesEntity_label_locations',
            i18n_domain='PleiadesEntity',
        ),
        allowed_types=('Location',),
        multiValued=1,
        relationship='location_location'
    ),

    ReferenceField(
        name='names',
        widget=ReferenceWidget(
            label='Names',
            label_msgid='PleiadesEntity_label_names',
            i18n_domain='PleiadesEntity',
        ),
        allowed_types=('Name', 'EthnicName', 'GeographicName'),
        multiValued=1,
        relationship='name_name'
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Place_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Place(BaseContent):
    """Associates Names and Locations
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Ancient Place'

    meta_type = 'Place'
    portal_type = 'Place'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    content_icon = 'place_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Ancient Place"
    typeDescMsgId = 'description_edit_place'

    _at_rename_after_creation = True

    schema = Place_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    # Manually created methods

    security.declareProtected(DEFAULT_ADD_CONTENT_PERMISSION, 'invokeFactory')
    def invokeFactory(self):
        """
        """
        pass


registerType(Place, PROJECTNAME)
# end of class Place

##code-section module-footer #fill in your manual code here
##/code-section module-footer



