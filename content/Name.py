# -*- coding: utf-8 -*-
#
# File: Name.py
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

# additional imports from tagged value 'import'
from Products.PleiadesEntity.Extensions.cooking import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='title',
        widget=StringWidget(
            label="Transliterated Name",
            description="A transliteration into the ASCII character set of the the attested name.",
            label_msgid='PleiadesEntity_label_title',
            description_msgid='PleiadesEntity_help_title',
            i18n_domain='PleiadesEntity',
        )
    ),

    StringField(
        name='nameAttested',
        index="FieldIndex",
        widget=StringWidget(
            label="Name as Attested",
            description="This field contains a transcription of the attested form of the name, in its original language and script.",
            label_msgid='PleiadesEntity_label_nameAttested',
            description_msgid='PleiadesEntity_help_nameAttested',
            i18n_domain='PleiadesEntity',
        )
    ),

    StringField(
        name='nameLanguage',
        index="FieldIndex",
        widget=StringWidget(
            label="Language and Writing System of Attested Name",
            description="This field indicates the language and writing system (script) of the attested name.",
            label_msgid='PleiadesEntity_label_nameLanguage',
            description_msgid='PleiadesEntity_help_nameLanguage',
            i18n_domain='PleiadesEntity',
        )
    ),

    StringField(
        name='accuracy',
        widget=SelectionWidget(
            label='Accuracy',
            label_msgid='PleiadesEntity_label_accuracy',
            i18n_domain='PleiadesEntity',
        ),
        enforceVocabulary=1,
        vocabulary= ['accurate', 'inaccurate', 'false']
    ),

    StringField(
        name='completeness',
        widget=SelectionWidget(
            label='Completeness',
            label_msgid='PleiadesEntity_label_completeness',
            i18n_domain='PleiadesEntity',
        ),
        enforceVocabulary=1,
        vocabulary= ['complete', 'fragmentary, but reconstructable', 'fragmentary and not reconstructable']
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Name_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Name(BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Ancient Name'

    meta_type = 'Name'
    portal_type = 'Name'
    allowed_content_types = ['TemporalAttestation', 'Reference', 'SecondaryReference', 'PrimaryReference']
    filter_content_types = 1
    global_allow = 0
    content_icon = 'document_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Any sort of name that can be applied to a geographic place."
    typeDescMsgId = 'description_edit_name'

    _at_rename_after_creation = True

    schema = Name_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(Name, PROJECTNAME)
# end of class Name

##code-section module-footer #fill in your manual code here
##/code-section module-footer


