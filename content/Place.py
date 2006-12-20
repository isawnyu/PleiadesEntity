# ===========================================================================
# Copyright (c) 2006 by Ancient World Mapping Center, University of North
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
from Products.PleiadesEntity.Extensions.cooking import *

##code-section module-header #fill in your manual code here
##/code-section module-header

copied_fields = {}
copied_fields['title'] = BaseSchema['title'].copy()
copied_fields['title'].widget.label = "Identifier"
copied_fields['title'].widget.description = "Unique Pleiades identifier for this place."
schema = Schema((

    copied_fields['title'],
        StringField(
        name='placeType',
        index="FieldIndex",
        widget=StringWidget(
            label="Place Type",
            label_msgid='PleiadesEntity_label_placeType',
            i18n_domain='PleiadesEntity',
        )
    ),

    TextField(
        name='modernLocation',
        index="ZCTextIndex",
        widget=TextAreaWidget(
            label="Modern Name / Location",
            description="A prose description, in modern terms, of this entity's location.",
            label_msgid='PleiadesEntity_label_modernLocation',
            description_msgid='PleiadesEntity_help_modernLocation',
            i18n_domain='PleiadesEntity',
        )
    ),

    LinesField(
        name='timePeriods',
        index="KeywordIndex",
        widget=LinesWidget(
            label="Time Periods",
            description="Standard time periods during which this entity is believed to have been an active concern.",
            label_msgid='PleiadesEntity_label_timePeriods',
            description_msgid='PleiadesEntity_help_timePeriods',
            i18n_domain='PleiadesEntity',
        )
    ),

    LinesField(
        name='secondaryReferences',
        index="KeywordIndex",
        widget=LinesWidget(
            label="Secondary References",
            description="Citations for works of modern scholarship that provide substantive information about this entity.",
            label_msgid='PleiadesEntity_label_secondaryReferences',
            description_msgid='PleiadesEntity_help_secondaryReferences',
            i18n_domain='PleiadesEntity',
        )
    ),

    StringField(
        name='spatialCoordinates',
        widget=StringWidget(
            label="Spatial Coordinates",
            label_msgid='PleiadesEntity_label_spatialCoordinates',
            i18n_domain='PleiadesEntity',
        )
    ),

    StringField(
        name='spatialGeometryType',
        default="point",
        index="FieldIndex",
        widget=StringWidget(
            label="Spatial Geometry Type",
            label_msgid='PleiadesEntity_label_spatialGeometryType',
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
    archetype_name = 'Place'

    meta_type = 'Place'
    portal_type = 'Place'
    allowed_content_types = ['Name']
    filter_content_types = 1
    global_allow = 1
    content_icon = 'place_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = """A "place" is an association (grouping) of geographic names and geographic locations, encompassing both place points and larger regions (i.e., we call a space a place)"""
    typeDescMsgId = 'description_edit_place'

    _at_rename_after_creation = True

    schema = Place_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    # Manually created methods

    security.declarePrivate('at_post_edit_script')
    def at_post_edit_script(self):
        """
        """

        self.at_post_create_script()

    security.declarePrivate('at_post_create_script')
    def at_post_create_script(self):
        """
        """

        newID = setIdFromTitle(self)



registerType(Place, PROJECTNAME)
# end of class Place

##code-section module-footer #fill in your manual code here
##/code-section module-footer



