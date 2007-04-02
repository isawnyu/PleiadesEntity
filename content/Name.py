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
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.PleiadesEntity.config import *

##code-section module-header #fill in your manual code here
from Products.CMFCore.permissions import View
from Products.PleiadesEntity.Extensions.ws_validation import validate_name
from Products.PleiadesEntity.Extensions.ws_transliteration import transliterate_name
##/code-section module-header

schema = Schema((

    StringField(
        name='nameAttested',
        index="ZCTextIndex",
        widget=StringWidget(
            label="Name as Attested",
            description="A transcription of the attested form of the name, in its original language and script.",
            macro="nameattested_widget",
            label_msgid='PleiadesEntity_label_nameAttested',
            description_msgid='PleiadesEntity_help_nameAttested',
            i18n_domain='PleiadesEntity',
        )
    ),

    StringField(
        name='nameLanguage',
        index="FieldIndex",
        widget=SelectionWidget(
            label="Language and Writing System",
            description="The language and writing system (script) of the attested name.",
            label_msgid='PleiadesEntity_label_nameLanguage',
            description_msgid='PleiadesEntity_help_nameLanguage',
            i18n_domain='PleiadesEntity',
        ),
        vocabulary=NamedVocabulary("""ancient-name-languages"""),
        enforceVocabulary=1
    ),

    StringField(
        name='nameTransliterated',
        widget=StringWidget(
            label="Transliterated name",
            label_msgid='PleiadesEntity_label_nameTransliterated',
            i18n_domain='PleiadesEntity',
        )
    ),

    StringField(
        name='nameType',
        widget=SelectionWidget(
            label="Name type",
            label_msgid='PleiadesEntity_label_nameType',
            i18n_domain='PleiadesEntity',
        ),
        vocabulary=NamedVocabulary("""name-types"""),
        default="geographic",
        enforceVocabulary=1
    ),

    StringField(
        name='accuracy',
        index="FieldIndex",
        vocabulary=NamedVocabulary("""name-accuracy"""),
        default="accurate",
        enforceVocabulary=1,
        widget=SelectionWidget(
            label="Accuracy of Attestation",
            label_msgid='PleiadesEntity_label_accuracy',
            i18n_domain='PleiadesEntity',
        )
    ),

    StringField(
        name='completeness',
        index="FieldIndex",
        vocabulary=NamedVocabulary("""name-completeness"""),
        default="complete",
        enforceVocabulary=1,
        widget=SelectionWidget(
            label="Completeness of Attestation",
            label_msgid='PleiadesEntity_label_completeness',
            i18n_domain='PleiadesEntity',
        )
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
    allowed_content_types = ['TemporalAttestation', 'SecondaryReference', 'PrimaryReference']
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
    schema["title"].required = 0
    schema["title"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["nameTransliterated"].widget.visible = {"edit": "invisible", "view": "visible"}
    ##/code-section class-header

    # Methods

    security.declarePublic('getTimePeriods')
    def getTimePeriods(self):
        """
        """
        periods = []
        for ta in self.getFolderContents({'meta_type':['TemporalAttestation']}):
            periods.append(ta.getId)
        return periods

    security.declarePublic('setNameTransliterated')
    def setNameTransliterated(self,value):
        """
        """
        if len(value) == 0:
            REQUEST = self.REQUEST
            tNameLanguage = REQUEST.get('nameLanguage', None)
            tNameAttested = REQUEST.get('nameAttested', None)
            if tNameLanguage and tNameAttested:
                t = transliterate_name(tNameLanguage, tNameAttested)
            else:
                t = ''
        else:
            t = value
        self.getField('nameTransliterated').set(self, t)
        self.getField('title').set(self, t)

    security.declarePublic('setNameAttested')
    def setNameAttested(self,value):
        """
        """
        self.getField('nameAttested').set(self, value)
        self.setNameTransliterated('')

    # Manually created methods

    security.declareProtected(View, 'post_validate')
    def post_validate(self, REQUEST=None, errors=None):
        vNameLanguage = REQUEST.get('nameLanguage', None)
        vNameAttested = REQUEST.get('nameAttested', None)
        invalid = validate_name(vNameLanguage, vNameAttested)
        if len(invalid) > 0:
            errors['nameAttested'] = invalid



registerType(Name, PROJECTNAME)
# end of class Name

##code-section module-footer #fill in your manual code here
##/code-section module-footer



