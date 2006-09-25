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
from Products.GeographicEntityLite.config import *

# additional imports from tagged value 'import'
from Products.GeographicEntityLite.Extensions.cooking import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='identifier',
        widget=StringWidget(
            label="Identifier",
            label_msgid='GeographicEntityLite_label_identifier',
            i18n_domain='GeographicEntityLite',
        ),
        required=1
    ),

    StringField(
        name='geoEntityType',
        widget=StringWidget(
            label="Entity Type",
            label_msgid='GeographicEntityLite_label_geoEntityType',
            i18n_domain='GeographicEntityLite',
        )
    ),

    TextField(
        name='modernLocation',
        widget=TextAreaWidget(
            label="Modern Name / Location",
            label_msgid='GeographicEntityLite_label_modernLocation',
            i18n_domain='GeographicEntityLite',
        )
    ),

    LinesField(
        name='timePeriods',
        widget=LinesWidget(
            label="Time Periods",
            label_msgid='GeographicEntityLite_label_timePeriods',
            i18n_domain='GeographicEntityLite',
        )
    ),

    LinesField(
        name='secondaryReferences',
        widget=LinesWidget(
            label="Secondary References",
            label_msgid='GeographicEntityLite_label_secondaryReferences',
            i18n_domain='GeographicEntityLite',
        )
    ),

    StringField(
        name='spatialCoordinates',
        widget=StringWidget(
            label="Spatial Coordinates",
            label_msgid='GeographicEntityLite_label_spatialCoordinates',
            i18n_domain='GeographicEntityLite',
        )
    ),

    StringField(
        name='spatialGeometryType',
        default="point",
        widget=StringWidget(
            label="Spatial Geometry Type",
            label_msgid='GeographicEntityLite_label_spatialGeometryType',
            i18n_domain='GeographicEntityLite',
        )
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

GeographicEntityLite_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class GeographicEntityLite(BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Geographic Entity (Lite)'

    meta_type = 'GeographicEntityLite'
    portal_type = 'GeographicEntityLite'
    allowed_content_types = ['GeographicNameLite']
    filter_content_types = 1
    global_allow = 1
    content_icon = 'geoelite_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "A simple content type for storing information about geographic entities (features)."
    typeDescMsgId = 'description_edit_geographicentitylite'

    _at_rename_after_creation = False

    schema = GeographicEntityLite_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePrivate('at_post_create_script')
    def at_post_create_script(self):
        """
        """

        newID = setIdFromTitle(self)

    security.declarePrivate('at_post_edit_script')
    def at_post_edit_script(self):
        """
        """

        self.at_post_create_script()


registerType(GeographicEntityLite, PROJECTNAME)
# end of class GeographicEntityLite

##code-section module-footer #fill in your manual code here
##/code-section module-footer



