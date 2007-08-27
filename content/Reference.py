# -*- coding: utf-8 -*-
#
# File: Reference.py
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

from Products.Archetypes.Registry import registerWidget

class CitationItemWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({'macro': 'referenceitem_widget'})

registerWidget(
    CitationItemWidget,
    title='String',
    description='Renders a citation item, with link',
    used_for=('Products.Archetypes.Field.StringField',)
    )

##/code-section module-header

copied_fields = {}
copied_fields['title'] = BaseSchema['title'].copy()
copied_fields['title'].widget.label = "Citation"
schema = Schema((

    copied_fields['title'],
        StringField(
        name='item',
        widget=CitationItemWidget(
            label='Citation item',
            label_msgid='PleiadesEntity_label_item',
            i18n_domain='PleiadesEntity',
        )
    ),

    StringField(
        name='range',
        widget=StringWidget(
            label="Citation range",
            label_msgid='PleiadesEntity_label_range',
            i18n_domain='PleiadesEntity',
        )
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Reference_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Reference(BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Bibliographic Reference'

    meta_type = 'Reference'
    portal_type = 'Reference'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 1
    #content_icon = 'Reference.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Bibliographic Reference"
    typeDescMsgId = 'description_edit_reference'

    _at_rename_after_creation = True

    schema = Reference_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(Reference, PROJECTNAME)
# end of class Reference

##code-section module-footer #fill in your manual code here
##/code-section module-footer



