# -*- coding: utf-8 -*-
#
# File: Work.py
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
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CompoundField.ArrayField import ArrayField
from Products.CompoundField.CompoundWidget import CompoundWidget
from Products.CompoundField.EnhancedArrayWidget import EnhancedArrayWidget
from Products.PleiadesEntity.config import *
from Products.PleiadesEntity.content.ReferenceCitation import ReferenceCitation
from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implementer
from .interfaces import IWork

##code-section module-header #fill in your manual code here
##/code-section module-header

@implementer(IValidator)
class ReferencesValidator(object):

    name = 'referencesvalidator'

    def __call__(self, value, instance, *args, **kwargs):
        # Check that ranges of all attestations are not empty
        if not len(value.get('short_title', '')):
            return "Reference is missing title"
        return True

schema = Schema((

    ArrayField(
        ReferenceCitation(
            name='referenceCitations',
            widget=CompoundWidget(
                label="Reference (Citation)",
                label_msgid='PleiadesEntity_label_referenceCitations',
                i18n_domain='PleiadesEntity',
            ),
            description="External entity cited",
            multiValued=True,
            validators=(
                ReferencesValidator(),)
        ),

        widget=EnhancedArrayWidget(
            label="References",
            description='Add or remove citations of other works. Follow the '
                'instructions in the <a '
                'href="/help/editorial-guidelines">Editorial Guidelines</a> '
                'and the <a '
                'href="/help/citation-guide">Citation Guide.</a>',
            macro="pleiadescitationrefwidget",
            label_msgid='PleiadesEntity_label_array:referenceCitations',
            description_msgid='PleiadesEntity_help_array:referenceCitations',
            i18n_domain='PleiadesEntity',
        ),
        size=0,
        schemata="References",
    ),

    StringField(
        name='initialProvenance',
        widget=StringField._properties['widget'](
            label="Initial Provenance",
            description="The origin of this entity.",
            label_msgid='PleiadesEntity_label_initialProvenance',
            description_msgid='PleiadesEntity_help_initialProvenance',
            i18n_domain='PleiadesEntity',
        ),
        searchable=True,
        required=0,
        default="Pleiades"
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Work_schema = schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

@implementer(IWork)
class Work(BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    _at_rename_after_creation = True

    schema = Work_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('rangesText')
    def rangesText(self):
        return  "; ".join([c.get('short_title', '') + ' ' +
                           c.get('citation_detail', '') for c in self.getReferenceCitations()])

    security.declarePublic('Cites')
    def Cites(self):
        return self.rangesText()

    security.declarePublic('Provenance')
    def Provenance(self):
        return self.getInitialProvenance()

    security.declarePublic('getCitationTypes')
    def getCitationTypes(self):
        return dict(ReferenceCitation.schema["type"].vocabulary)

    security.declarePublic('getSortedReferenceCitations')
    def getSortedReferenceCitations(self):
        vocab = self.getCitationTypes()

        refs = []
        transformer = getToolByName(self, 'portal_transforms').convertTo
        for r in self.getReferenceCitations():
            ref = r.copy()
            ref['gloss'] = unicode(str(
                transformer('text/plain',
                            ref.get('formatted_citation', ''),
                            mimetype='text/html')), 'utf-8')
            title = unicode(ref.get('short_title', ''), 'utf-8')
            text = unicode(ref.get('citation_detail', ''), 'utf-8')
            if title:
                text = title + ' ' + text
            if not text:
                text = ref['gloss']
            ref['text'] = text
            refs.append(ref)

        refs.sort(key=lambda r: r.get('text', ''))

        groups = []
        for key in vocab.keys():
            partial = [r for r in refs if r.get('type', 'seeFurther') == key]
            if partial:
                label = vocab[key]
                if isinstance(label, unicode):
                    label = label.encode('utf-8')
                groups.append((vocab[key], partial))

        return groups

# end of class Work

##code-section module-footer #fill in your manual code here
##/code-section module-footer



