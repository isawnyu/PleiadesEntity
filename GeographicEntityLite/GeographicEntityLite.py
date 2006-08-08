# File: GeographicEntityLite.py
#
# Copyright (c) 2006 by []
# Generator: ArchGenXML Version 1.4.1
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

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.GeographicEntityLite.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='awmcID',
        widget=StringWidget(
            label="AWMC Inventory Number",
            label_msgid='GeographicEntityLite_label_awmcID',
            i18n_domain='GeographicEntityLite',
        )
    ),

    StringField(
        name='bAtlasMap',
        widget=SelectionWidget(
            label="Barrington Atlas Map Number",
            label_msgid='GeographicEntityLite_label_bAtlasMap',
            i18n_domain='GeographicEntityLite',
        ),
        vocabulary=NamedVocabulary("""bAtlasMapNumbers""")
    ),

    StringField(
        name='bAtlasGrid',
        widget=StringWidget(
            label="Barrington Atlas Grid Reference",
            label_msgid='GeographicEntityLite_label_bAtlasGrid',
            i18n_domain='GeographicEntityLite',
        )
    ),

    StringField(
        name='geoEntityType',
        widget=SelectionWidget(
            label="Entity Type",
            label_msgid='GeographicEntityLite_label_geoEntityType',
            i18n_domain='GeographicEntityLite',
        ),
        vocabulary=NamedVocabulary("""geographictype""")
    ),

    StringField(
        name='modernLocation',
        widget=StringWidget(
            label="Modern Name / Location",
            label_msgid='GeographicEntityLite_label_modernLocation',
            i18n_domain='GeographicEntityLite',
        )
    ),

    StringField(
        name='timePeriods',
        widget=StringWidget(
            label="Time Periods",
            label_msgid='GeographicEntityLite_label_timePeriods',
            i18n_domain='GeographicEntityLite',
        )
    ),

    StringField(
        name='references',
        widget=StringWidget(
            label="References",
            label_msgid='GeographicEntityLite_label_references',
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

GeographicEntityLite_schema = OrderedBaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class GeographicEntityLite(OrderedBaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(OrderedBaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'GeographicEntityLite'

    meta_type = 'GeographicEntityLite'
    portal_type = 'GeographicEntityLite'
    allowed_content_types = ['GeographicNameLite']
    filter_content_types = 1
    global_allow = 1
    allow_discussion = False
    #content_icon = 'GeographicEntityLite.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "GeographicEntityLite"
    typeDescMsgId = 'description_edit_geographicentitylite'

    schema = GeographicEntityLite_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(GeographicEntityLite,PROJECTNAME)
# end of class GeographicEntityLite

##code-section module-footer #fill in your manual code here
##/code-section module-footer



