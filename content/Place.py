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
        default="unknown",
        index="KeywordIndex",
        widget=SelectionWidget(
            label="Place Type",
            label_msgid='PleiadesEntity_label_placeType',
            i18n_domain='PleiadesEntity',
        ),
        enforceVocabulary=1,
        vocabulary=['aqueduct', 'bath', 'bay', 'bridge', 'canal', 'cape', 'cave', 'cemetery', 'centuriation', 'church', 'coast', 'dam', 'estate', 'estuary', 'findspot', 'forest', 'fort', 'hill', 'island', 'lighthouse', 'mine', 'mountain', 'oasis', 'pass', 'people', 'plain', 'port', 'production', 'region', 'reservoir', 'ridge', 'river', 'road', 'salt-marsh', 'settlement', 'settlement-modern', 'spring', 'station', 'temple', 'tumulus', 'unknown', 'unlocated', 'valley', 'wall', 'water-inland', 'water-open', 'well', 'wheel', 'whirlpool']
    ),

    StringField(
        name='modernLocation',
        index="ZCTextIndex",
        widget=StringWidget(
            label="Modern Location",
            description="An indication in prose of the modern location and vicinity of the ancient place.",
            label_msgid='PleiadesEntity_label_modernLocation',
            description_msgid='PleiadesEntity_help_modernLocation',
            i18n_domain='PleiadesEntity',
        )
    ),

    StringField(
        name='certainty',
        widget=SelectionWidget(
            label="Certainty of association",
            description="Certainty of association between locations and names",
            label_msgid='PleiadesEntity_label_certainty',
            description_msgid='PleiadesEntity_help_certainty',
            i18n_domain='PleiadesEntity',
        ),
        vocabulary=["certain", "less certain", "uncertain"]
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

Place_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
del Place_schema['title']
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
    allowed_content_types = ['SecondaryReference']
    filter_content_types = 1
    global_allow = 0
    content_icon = 'place_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Associates Names and Locations"
    typeDescMsgId = 'description_edit_place'

    _at_rename_after_creation = False

    schema = Place_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('get_title')
    def get_title(self):
        """Return a title string derived from the ancient names to which
        this place refers.
        """
        # Dodge a reference_catalog quirk
        try:
            names = self.getRefs('name_name')
            if names:
                return '/'.join([n.Title() for n in names])
            else:
                return "Unnamed %s" % self.getPlaceType().capitalize()
        except AttributeError:
            return 'Unnamed Place'

    security.declarePublic('Title')
    def Title(self):
        """
        """
        return self.get_title()

    security.declarePublic('getTimePeriods')
    def getTimePeriods(self):
        """
        """
        names = self.getRefs('name_name')
        locations = self.getRefs('location_location')
        periods = []
        for name in names:
            periods.extend(name.getTimePeriods())
        for location in locations:
            periods.extend(location.getTimePeriods())
        result = []
        for p in periods:
            if p not in result:
                result.append(p)
        return result


registerType(Place, PROJECTNAME)
# end of class Place

##code-section module-footer #fill in your manual code here
##/code-section module-footer



