# File: GeographicNameLite.py
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
from Products.GeographicEntityLite.config import *

##code-section module-header #fill in your manual code here
from Products.Archetypes.utils import DisplayList
from Products.PloneLanguageTool import LanguageTool
from Products.CMFCore.utils import getToolByName
import sys,logging
import operator
##/code-section module-header

schema = Schema((

    StringField(
        name='nameString',
        widget=StringWidget(
            label="Name as Attested",
            label_msgid='GeographicEntityLite_label_nameString',
            i18n_domain='GeographicEntityLite',
        ),
        required=1
    ),

    StringField(
        name='nameLanguage',
        widget=SelectionWidget(
            label="Language and Writing System of Attested Name",
            label_msgid='GeographicEntityLite_label_nameLanguage',
            i18n_domain='GeographicEntityLite',
        ),
        vocabulary= 'trelanguages'
    ),

    BooleanField(
        name='certain',
        default="0",
        widget=BooleanWidget(
            label='Certain',
            label_msgid='GeographicEntityLite_label_certain',
            i18n_domain='GeographicEntityLite',
        )
    ),

    BooleanField(
        name='modern',
        default="0",
        widget=BooleanWidget(
            label="Name is Modern",
            label_msgid='GeographicEntityLite_label_modern',
            i18n_domain='GeographicEntityLite',
        )
    ),

    BooleanField(
        name='inaccurate',
        default="0",
        widget=BooleanWidget(
            label='Inaccurate',
            label_msgid='GeographicEntityLite_label_inaccurate',
            i18n_domain='GeographicEntityLite',
        )
    ),

    BooleanField(
        name='inferred',
        default="0",
        widget=BooleanWidget(
            label='Inferred',
            label_msgid='GeographicEntityLite_label_inferred',
            i18n_domain='GeographicEntityLite',
        )
    ),

    BooleanField(
        name='reconstructed',
        default="0",
        widget=BooleanWidget(
            label='Reconstructed',
            label_msgid='GeographicEntityLite_label_reconstructed',
            i18n_domain='GeographicEntityLite',
        )
    ),

    BooleanField(
        name='fragmentary',
        default="0",
        widget=BooleanWidget(
            label='Fragmentary',
            label_msgid='GeographicEntityLite_label_fragmentary',
            i18n_domain='GeographicEntityLite',
        )
    ),

    BooleanField(
        name='abbreviated',
        default="0",
        widget=BooleanWidget(
            label='Abbreviated',
            label_msgid='GeographicEntityLite_label_abbreviated',
            i18n_domain='GeographicEntityLite',
        )
    ),

    LinesField(
        name='primaryReferences',
        widget=LinesWidget(
            label="Primary References",
            label_msgid='GeographicEntityLite_label_primaryReferences',
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

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

GeographicNameLite_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class GeographicNameLite(BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Geographic Name (Lite)'

    meta_type = 'GeographicNameLite'
    portal_type = 'GeographicNameLite'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    allow_discussion = False
    content_icon = 'geonlite_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Geographic Name (Lite)"
    typeDescMsgId = 'description_edit_geographicnamelite'

    _at_rename_after_creation = True

    schema = GeographicNameLite_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    # Manually created methods

    def trelanguages(self):
        """
        Get a display list of language codes and associated names 
        derived from the languages selected as 'supported' in the Plone Language Tool
        """
        # get a reference to the Plone Language Tool so we can access its methods
        ltoolid = LanguageTool.id
        ltool = getToolByName(self, ltoolid, None)
        if ltool is None:
            return None
            
        # request the entire dictionary of available languages from the plone language tool
        # (the other, more specific, methods don't return all the data we would like to have access to)
        langs = ltool.getAvailableLanguageInformation()
        
        # build a list of language tuples, where the first item in each tuple is the ISO language code
        # and the second item is a language name string, made as sensible as possible to all users
        # Ideally, we'd like to have first the native form of the language name (if known/appropriate),
        # followed by the name of that language in the language/locale of the current user. But
        # the PLT doesn't support this configuration (it does only native/english), so we'd have to add 
        # alot of functionality here to get what we want -- better to patch the PLT eventually?
        supported_langs = []
        for lang_code, lang_info in langs.iteritems():
            if lang_info['selected']:
                if lang_info.has_key('native') and lang_info.has_key('english'):
                    if lang_info['native'] != lang_info['english']:
                        lang_name = lang_info['native'] + ' / ' + lang_info['english']
                    else:
                        lang_name = lang_info['native']
                elif lang_info.has_key('native'):
                    lang_name = lang_info['native']
                elif lang_info.has_key('english'):
                    lang_name = lang_info['english']
                else:
                    lang_name = 'language without a name'
                scruple = (lang_code, lang_name)
                supported_langs.append(scruple)
                
        return DisplayList(sorted(supported_langs, key=operator.itemgetter(1)))
                


registerType(GeographicNameLite,PROJECTNAME)
# end of class GeographicNameLite

##code-section module-footer #fill in your manual code here


##/code-section module-footer



