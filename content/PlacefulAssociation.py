# -*- coding: utf-8 -*-
#
# File: PlacefulAssociation.py
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
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.PleiadesEntity.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='placeType',
        index="KeywordIndex",
        vocabulary=NamedVocabulary("""AWMCPlaceTypes"""),
        default="unknown",
        enforceVocabulary=1,
        widget=SelectionWidget(
            label="Place Type",
            label_msgid='PleiadesEntity_label_placeType',
            i18n_domain='PleiadesEntity',
        )
    ),

    StringField(
        name='associationCertainty',
        widget=SelectionWidget(
            label="Certainty of association",
            description="Certainty of association between locations and names",
            label_msgid='PleiadesEntity_label_associationCertainty',
            description_msgid='PleiadesEntity_help_associationCertainty',
            i18n_domain='PleiadesEntity',
        ),
        vocabulary=NamedVocabulary("""AWMCPlacefulAssociationCertainty"""),
        enforceVocabulary=1
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
        relationship='hasLocation'
    ),

    ReferenceField(
        name='names',
        widget=ReferenceWidget(
            label='Names',
            label_msgid='PleiadesEntity_label_names',
            i18n_domain='PleiadesEntity',
        ),
        allowed_types=('Name',),
        multiValued=1,
        relationship='hasName'
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlacefulAssociation_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlacefulAssociation(BaseFolder):
    """Associates Names and Locations
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'PlacefulAssociation'

    meta_type = 'PlacefulAssociation'
    portal_type = 'PlacefulAssociation'
    allowed_content_types = ['SecondaryReference']
    filter_content_types = 1
    global_allow = 0
    content_icon = 'place_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "PlacefulAssociation"
    typeDescMsgId = 'description_edit_placefulassociation'

    _at_rename_after_creation = False

    schema = PlacefulAssociation_schema

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
            names = self.getRefs('hasName')
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
        names = self.getRefs('hasName')
        locations = self.getRefs('hasLocation')
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


registerType(PlacefulAssociation, PROJECTNAME)
# end of class PlacefulAssociation

##code-section module-footer #fill in your manual code here
##/code-section module-footer



