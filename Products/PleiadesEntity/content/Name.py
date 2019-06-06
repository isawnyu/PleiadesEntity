# -*- coding: utf-8 -*-
#
# File: Name.py
#
# Copyright (c) 2009 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
# Generator: ArchGenXML Version 2.4.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Sean Gillies <unknown>, Tom Elliott <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.component import queryUtility
from zope.interface import implements
import interfaces
from Products.PleiadesEntity.content.Work import Work
from Products.PleiadesEntity.content.Temporal import Temporal
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFPlone.utils import safe_unicode

from Products.CompoundField.ArrayField import ArrayField
from Products.CompoundField.EnhancedArrayWidget import EnhancedArrayWidget
from Products.PleiadesEntity.config import *

from Products.CompoundField.CompoundWidget import CompoundWidget
from Products.PleiadesEntity.content.ReferenceCitation import ReferenceCitation

from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.ATContentTypes.content import schemata
try:
    from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
    from plone.i18n.normalizer.interfaces import IURLNormalizer
    URL_NORMALIZER = True
except ImportError:
    URL_NORMALIZER = False


schema = Schema((

    StringField(
        name='nameAttested',
        schemata="Transcription",
        widget=StringField._properties['widget'](
            label="Name as attested",
            description="Enter transcription of the attested form of the name in its original language and script, if known.",
            macro="nameattested_widget",
            size=60,
            label_msgid='PleiadesEntity_label_nameAttested',
            description_msgid='PleiadesEntity_help_nameAttested',
            i18n_domain='PleiadesEntity',
        ),
        description="A transcription of the attested form of the name, in its original language and script.",
        searchable=True,
        required=0,
    ),
    StringField(
        name='nameLanguage',
        schemata="Transcription",
        widget=SelectionWidget(
            label="Language",
            description="Select the language and writing system or script of the attested name above.",
            label_msgid='PleiadesEntity_label_nameLanguage',
            description_msgid='PleiadesEntity_help_nameLanguage',
            i18n_domain='PleiadesEntity',
        ),
        description="The language and writing system or script of the attested name.",
        vocabulary_factory='pleiades.vocabularies.ancient_name_languages',
        enforceVocabulary=1,
        required=1,
    ),
    StringField(
        name='nameTransliterated',
        widget=StringField._properties['widget'](
            label="Romanized Name(s)",
            description="A comma-separated list of romanized forms of the name. The first will become the title of this resource.",
            size=130,
            label_msgid='PleiadesEntity_label_nameTransliterated',
            description_msgid='PleiadesEntity_help_nameTransliterated',
            i18n_domain='PleiadesEntity',
        ),
        searchable=True,
        required=1,
    ),
    StringField(
        name='nameType',
        widget=SelectionWidget(
            label="Name type",
            description="Select type of name",
            label_msgid='PleiadesEntity_label_nameType',
            description_msgid='PleiadesEntity_help_nameType',
            i18n_domain='PleiadesEntity',
        ),
        description="Type of name",
        vocabulary_factory='pleiades.vocabularies.name_types',
        default="geographic",
        enforceVocabulary=1,
    ),
    StringField(
        name='accuracy',
        schemata="Transcription",
        widget=SelectionWidget(
            label="Accuracy of transcription",
            description="Select level of transcription accuracy",
            label_msgid='PleiadesEntity_label_accuracy',
            description_msgid='PleiadesEntity_help_accuracy',
            i18n_domain='PleiadesEntity',
        ),
        description="Level of accuracy of transcription",
        vocabulary_factory='pleiades.vocabularies.name_accuracy',
        default="accurate",
        enforceVocabulary=1,
    ),
    StringField(
        name='completeness',
        schemata="Transcription",
        widget=SelectionWidget(
            label="Level of transcription completeness",
            description="Select level of transcription completeness",
            label_msgid='PleiadesEntity_label_completeness',
            description_msgid='PleiadesEntity_help_completeness',
            i18n_domain='PleiadesEntity',
        ),
        description="Level of completeness of transcription",
        vocabulary_factory='pleiades.vocabularies.name_completeness',
        default="complete",
        enforceVocabulary=1,
    ),
    StringField(
        name='associationCertainty',
        widget=SelectionWidget(
            label="Level of certainty in association between name and the place",
            description="Select level of certainty in association between name and feature",
            label_msgid='PleiadesEntity_label_associationCertainty',
            description_msgid='PleiadesEntity_help_associationCertainty',
            i18n_domain='PleiadesEntity',
        ),
        description="Level of certainty in association between name and feature",
        vocabulary_factory='pleiades.vocabularies.association_certainty',
        default="certain",
        enforceVocabulary=1,
    ),
    ArrayField(
        ReferenceCitation(
            name='primaryReferenceCitations',
            widget=CompoundWidget(
                label="Reference work and citation range",
                label_msgid='PleiadesEntity_label_primaryReferenceCitations',
                i18n_domain='PleiadesEntity',
            ),
            description="Reference work and citation range",
            searchable=True,
            multiValued=True,
        ),

        widget=EnhancedArrayWidget(
            label="Primary reference citations",
            description="Enter reference work and citation range",
            macro="pleiadescitationrefwidget",
            label_msgid='PleiadesEntity_label_array:primaryReferenceCitations',
            description_msgid='PleiadesEntity_help_array:primaryReferenceCitations',
            i18n_domain='PleiadesEntity',
        ),
        size=0,
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

##code-section after-schema #fill in your manual code here
Name_schema = ATDocumentSchema.copy() + \
    schema.copy() + \
    getattr(Temporal, 'schema', Schema(())).copy() + \
    getattr(Work, 'schema', Schema(())).copy()
##/code-section after-schema

off = {"edit": "invisible", "view": "invisible"}

schema = Name_schema

schema["title"].required = 0
schema["title"].widget.visible = off

schema["effectiveDate"].widget.visible = off
schema["expirationDate"].widget.visible = off
schema["allowDiscussion"].widget.visible = off
schema["excludeFromNav"].widget.visible = off
schema["text"].widget.label = 'Details'
schema["presentation"].widget.visible = off
schema["tableContents"].widget.visible = off
schema["primaryReferenceCitations"].widget.visible = off

schema["text"].schemata = "Details"

schema.moveField('nameAttested', pos='top')
schema.moveField('nameLanguage', after='nameAttested')    
schema.moveField('nameTransliterated', pos='top')
schema.moveField('text', pos='bottom')

schemata.finalizeATCTSchema(
    Name_schema,
    folderish=False,
    moveDiscussion=False
)

class Name(BaseContent, Work, Temporal, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IName)

    meta_type = 'Name'
    _at_rename_after_creation = True

    schema = Name_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    def generateNewId(self):
        title = self.getNameTransliterated()
        title = title.split(",")[0].strip() or "Untitled"
        # Don't do anything without the plone.i18n package
        if not URL_NORMALIZER:
            return None

        title = safe_unicode(title)
        request = getattr(self, 'REQUEST', None)
        if request is not None:
            return IUserPreferredURLNormalizer(request).normalize(title)

        return queryUtility(IURLNormalizer).normalize(title)

    security.declarePublic('SearchableText')
    def SearchableText(self):
        text = super(Name, self).SearchableText().strip()
        return text + ' ' + self.rangesText()

    # Manually created methods

registerType(Name, PROJECTNAME)
# end of class Name

##code-section module-footer #fill in your manual code here
##/code-section module-footer



