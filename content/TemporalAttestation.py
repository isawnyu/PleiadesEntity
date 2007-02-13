# -*- coding: utf-8 -*-
#
# File: TemporalAttestation.py
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
        name='certainty',
        default="certain",
        index="FieldIndex:brains",
        widget=SelectionWidget(
            label='Certainty',
            label_msgid='PleiadesEntity_label_certainty',
            i18n_domain='PleiadesEntity',
        ),
        enforceVocabulary=1,
        vocabulary=['certain', 'certain, but there is no contemporary evidence', 'less certain', 'less certain and there is no contemporary evidence']
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

TemporalAttestation_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class TemporalAttestation(BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Temporal Attestation'

    meta_type = 'TemporalAttestation'
    portal_type = 'TemporalAttestation'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    #content_icon = 'TemporalAttestation.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Temporal Attestation"
    typeDescMsgId = 'description_edit_temporalattestation'

    _at_rename_after_creation = True

    schema = TemporalAttestation_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(TemporalAttestation, PROJECTNAME)
# end of class TemporalAttestation

##code-section module-footer #fill in your manual code here
##/code-section module-footer



