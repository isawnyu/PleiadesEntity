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
copied_fields['title'].widget.label = "Transliterated Name"
copied_fields['title'].widget.description = "A transliteration into the ASCII character set of the the attested name."
schema = Schema((

    copied_fields['title'],
        BooleanField(
        name='nameUncertain',
        widget=BooleanWidget(
            label="Uncertain",
            description="If checked, this field indicates some degree of uncertainty in the assignment of this attested name to the parent place.",
            label_msgid='PleiadesEntity_label_nameUncertain',
            description_msgid='PleiadesEntity_help_nameUncertain',
            i18n_domain='PleiadesEntity',
        )
    ),

    StringField(
        name='nameType',
        index="FieldIndex",
        widget=StringWidget(
            label="Name Type",
            label_msgid='PleiadesEntity_label_nameType',
            i18n_domain='PleiadesEntity',
        )
    ),

    LinesField(
        name='timePeriods',
        index="KeywordIndex",
        widget=LinesWidget(
            label="Time Periods",
            description="Standard time periods during which this name is believed to have been in use.",
            label_msgid='PleiadesEntity_label_timePeriods',
            description_msgid='PleiadesEntity_help_timePeriods',
            i18n_domain='PleiadesEntity',
        )
    ),

    BooleanField(
        name='nameInferred',
        widget=BooleanWidget(
            label="Inferred",
            description="If checked, this field indicates that the name is not attested during any of the possible periods, but has been inferred from a verified attestation in an earlier or later period.",
            label_msgid='PleiadesEntity_label_nameInferred',
            description_msgid='PleiadesEntity_help_nameInferred',
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

    BooleanField(
        name='nameInaccurate',
        widget=BooleanWidget(
            label="Inaccurate",
            description="If checked, this field indicates that the name is presented in its attested form, but is considered inaccurate.",
            label_msgid='PleiadesEntity_label_nameInaccurate',
            description_msgid='PleiadesEntity_help_nameInaccurate',
            i18n_domain='PleiadesEntity',
        )
    ),

    BooleanField(
        name='nameAbbreviated',
        widget=BooleanWidget(
            label="Abbreviated",
            description="If checked, this field indicates that the name, as attested, is abbreviated and the full form does not appear in the historical record.",
            label_msgid='PleiadesEntity_label_nameAbbreviated',
            description_msgid='PleiadesEntity_help_nameAbbreviated',
            i18n_domain='PleiadesEntity',
        )
    ),

    BooleanField(
        name='nameReconstructed',
        widget=BooleanWidget(
            label="Reconstructed",
            description="If checked, this field indicates that the name is attested only incompletely, but the missing characters have been supplied on a reliable basis.",
            label_msgid='PleiadesEntity_label_nameReconstructed',
            description_msgid='PleiadesEntity_help_nameReconstructed',
            i18n_domain='PleiadesEntity',
        )
    ),

    BooleanField(
        name='nameFragmentary',
        widget=BooleanWidget(
            label="Fragmentary",
            description="If checked, this field indicates that the name is attested only incompletely, and the missing characters cannot be supplemented with certainty.",
            label_msgid='PleiadesEntity_label_nameFragmentary',
            description_msgid='PleiadesEntity_help_nameFragmentary',
            i18n_domain='PleiadesEntity',
        )
    ),

    LinesField(
        name='primaryReferences',
        index="KeywordIndex",
        widget=LinesWidget(
            label="Primary References",
            description="Citations for primary sources in which this name appears.",
            label_msgid='PleiadesEntity_label_primaryReferences',
            description_msgid='PleiadesEntity_help_primaryReferences',
            i18n_domain='PleiadesEntity',
        )
    ),

    LinesField(
        name='secondaryReferences',
        index="KeywordIndex",
        widget=LinesWidget(
            label="Secondary References",
            description="Citations for works of modern scholarship in which this name is discussed.",
            label_msgid='PleiadesEntity_label_secondaryReferences',
            description_msgid='PleiadesEntity_help_secondaryReferences',
            i18n_domain='PleiadesEntity',
        )
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Name_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Name(BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Name'

    meta_type = 'Name'
    portal_type = 'Name'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    content_icon = 'name_icon.gif'
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

        newID=setIdFromTitle(self)



registerType(Name, PROJECTNAME)
# end of class Name

##code-section module-footer #fill in your manual code here
##/code-section module-footer



