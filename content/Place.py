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
        name='modernLocation',
        index="ZCTextIndex",
        widget=StringWidget(
            label="Modern Location",
            description="The modern location or vicinity of the ancient place",
            label_msgid='PleiadesEntity_label_modernLocation',
            description_msgid='PleiadesEntity_help_modernLocation',
            i18n_domain='PleiadesEntity',
        )
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Place_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Place(BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Ancient Place'

    meta_type = 'Place'
    portal_type = 'Place'
    allowed_content_types = ['PlacefulAssociation']
    filter_content_types = 1
    global_allow = 0
    content_icon = 'place_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Ancient Place"
    typeDescMsgId = 'description_edit_place'

    _at_rename_after_creation = False

    schema = Place_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('Title')
    def Title(self):
        """
        """
        try:
            associations = self.listFolderContents()
            return '/'.join([a.Title() for a in associations if not a.Title().startswith('Unnamed')])
        except AttributeError:
            return 'Unnamed Place'

    security.declarePublic('getTimePeriods')
    def getTimePeriods(self):
        """
        """
        result = []
        for a in self.listFolderContents():
            for p in a.getTimePeriods():
                if p not in result:
                    result.append(p)
        return result

    security.declarePublic('getPlaceType')
    def getPlaceType(self):
        """
        """
        result = []
        for a in self.listFolderContents():
            if a.getPlaceType() not in result:
                result.append(a.getPlaceType())
        return result


registerType(Place, PROJECTNAME)
# end of class Place

##code-section module-footer #fill in your manual code here
##/code-section module-footer



