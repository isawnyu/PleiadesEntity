# -*- coding: utf-8 -*-
#
# File: Name.py
#
# Copyright (c) 2009 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
# Generator: ArchGenXML Version 2.3
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Sean Gillies <unknown>, Tom Elliott <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces
from Products.PleiadesEntity.content.Work import Work
from Products.PleiadesEntity.content.Temporal import Temporal
from Products.PleiadesEntity.content.Work import Work
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema

from Products.CompoundField.ArrayField import ArrayField
from Products.CompoundField.ArrayWidget import ArrayWidget
from Products.CompoundField.EnhancedArrayWidget import EnhancedArrayWidget
from Products.CompoundField.EnhancedArrayWidget import EnhancedArrayWidget
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.PleiadesEntity.config import *

# additional imports from tagged value 'import'
from Products.CMFCore import permissions
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.CompoundField.CompoundWidget import CompoundWidget
from Products.PleiadesEntity.content.ReferenceCitation import ReferenceCitation

##code-section module-header #fill in your manual code here
from Products.PleiadesEntity.content.ReferenceCitation import ReferenceCitation
from Products.PleiadesEntity.Extensions.ws_validation import validate_name
from Products.CMFCore import permissions
import transaction
from pleiades.transliteration import transliterate_name
##/code-section module-header

schema = Schema((

    StringField(
        name='nameAttested',
        widget=StringField._properties['widget'](
            label="Name as attested",
            description="Enter transcription of the attested form of the name, in its original language and script.",
            macro="nameattested_widget",
            label_msgid='PleiadesEntity_label_nameAttested',
            description_msgid='PleiadesEntity_help_nameAttested',
            i18n_domain='PleiadesEntity',
        ),
    ),
    StringField(
        name='nameLanguage',
        widget=SelectionWidget(
            label="Language and writing system",
            description="Select the language and writing system (script) of the attested name.",
            label_msgid='PleiadesEntity_label_nameLanguage',
            description_msgid='PleiadesEntity_help_nameLanguage',
            i18n_domain='PleiadesEntity',
        ),
        vocabulary=NamedVocabulary("""ancient-name-languages"""),
    ),
    StringField(
        name='nameTransliterated',
        widget=StringField._properties['widget'](
            label="Transliterated name",
            description="Enter transliteration of attested name",
            label_msgid='PleiadesEntity_label_nameTransliterated',
            description_msgid='PleiadesEntity_help_nameTransliterated',
            i18n_domain='PleiadesEntity',
        ),
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
        vocabulary=NamedVocabulary("""name-types"""),
    ),
    StringField(
        name='accuracy',
        widget=SelectionWidget(
            label="Accuracy of transcription",
            description="Select level of transcription accuracy",
            label_msgid='PleiadesEntity_label_accuracy',
            description_msgid='PleiadesEntity_help_accuracy',
            i18n_domain='PleiadesEntity',
        ),
        vocabulary=NamedVocabulary("""name-accuracy"""),
    ),
    StringField(
        name='completeness',
        widget=SelectionWidget(
            label="Level of transcription completeness",
            description="Select level of transcription completeness",
            label_msgid='PleiadesEntity_label_completeness',
            description_msgid='PleiadesEntity_help_completeness',
            i18n_domain='PleiadesEntity',
        ),
        vocabulary=NamedVocabulary("""name-completeness"""),
    ),
    StringField(
        name='associationCertainty',
        widget=SelectionWidget(
            label="Level of certainty in association between name and feature",
            description="Select level of certainty in association between name and feature",
            label_msgid='PleiadesEntity_label_associationCertainty',
            description_msgid='PleiadesEntity_help_associationCertainty',
            i18n_domain='PleiadesEntity',
        ),
        vocabulary=NamedVocabulary("""association-certainty"""),
    ),
    ArrayField(
        ReferenceCitation(
            name='primaryReferenceCitations',
            widget=CompoundWidget(
                label="Reference work and citation range",
                label_msgid='PleiadesEntity_label_primaryReferenceCitations',
                i18n_domain='PleiadesEntity',
            ),
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

Name_schema = ATDocumentSchema.copy() + \
    getattr(Work, 'schema', Schema(())).copy() + \
    getattr(Temporal, 'schema', Schema(())).copy() + \
    getattr(Work, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
Name_schema = ATDocumentSchema.copy() + \
    schema.copy() + \
    getattr(Temporal, 'schema', Schema(())).copy() + \
    getattr(Work, 'schema', Schema(())).copy()
##/code-section after-schema

class Name(ATDocument, Work, Temporal, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IName)

    meta_type = 'Name'
    _at_rename_after_creation = True

    schema = Name_schema

    ##code-section class-header #fill in your manual code here
    schema["title"].required = 0
    schema["title"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["nameTransliterated"].widget.visible = {"edit": "invisible", "view": "visible"}
    schema["text"].widget.label = 'Details'
    ##/code-section class-header

    # Methods

    security.declareProtected(permissions.AddPortalContent, '_renameAfterCreation')
    def _renameAfterCreation(self, check_auto_id=False):
        """
        """
        plone_tool = getToolByName(self, 'plone_utils', None)
        if plone_tool is None or not hasattr(plone_tool, 'normalizeString'):
            return None

        nameAttested = self.getNameAttested()
        nameLanguage = self.getNameLanguage()
        if not nameAttested or not nameLanguage:
            return False

        title = transliterate_name(nameLanguage, nameAttested)

        old_id = self.getId()
        if check_auto_id and not self._isIDAutoGenerated(old_id):
            # No auto generated id
            return False

        new_id = plone_tool.normalizeString(title)
        invalid_id = False
        check_id = getattr(self, 'check_id', None)
        if check_id is not None:
            invalid_id = check_id(new_id, required=1)
        else:
            # If check_id is not available just look for conflicting ids
            parent = aq_parent(aq_inner(self))
            invalid_id = new_id in parent.objectIds()

        if not invalid_id:
            # Can't rename without a subtransaction commit when using
            # portal_factory!
            transaction.commit(1)
            self.setId(new_id)
            return new_id

    security.declarePublic('SearchableText')
    def SearchableText(self):
        text = super(Name, self).SearchableText().strip()
        return text + ' ' + self.rangesText()

    # Manually created methods

    security.declareProtected(permissions.View, 'post_validate')
    def post_validate(self, REQUEST=None, errors=None):
        """
        """
        vNameLanguage = REQUEST.get('nameLanguage', None)
        vNameAttested = REQUEST.get('nameAttested', None)
        invalid = validate_name(vNameLanguage, vNameAttested)
        if len(invalid) > 0:
            errors['nameAttested'] = invalid



registerType(Name, PROJECTNAME)
# end of class Name

##code-section module-footer #fill in your manual code here
##/code-section module-footer



