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
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.CompoundField.ArrayField import ArrayField
from Products.CompoundField.ArrayWidget import ArrayWidget
from Products.CompoundField.EnhancedArrayWidget import EnhancedArrayWidget
from Products.CompoundField.EnhancedArrayWidget import EnhancedArrayWidget
from Products.PleiadesEntity.config import *

# additional imports from tagged value 'import'
from Products.CompoundField.CompoundWidget import CompoundWidget
from Products.CMFCore import permissions
from Products.PleiadesEntity.content.ReferenceCitation import ReferenceCitation

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    ArrayField(
        ReferenceCitation(
            name='referenceCitations',
            widget=CompoundWidget(
                label="Reference identifier and citation",
                label_msgid='PleiadesEntity_label_referenceCitations',
                i18n_domain='PleiadesEntity',
            ),
            description="External entity cited",
            multiValued=True,
        ),

        widget=EnhancedArrayWidget(
            label="References",
            description="Add or remove references cited by this entity",
            macro="pleiadescitationrefwidget",
            label_msgid='PleiadesEntity_label_array:referenceCitations',
            description_msgid='PleiadesEntity_help_array:referenceCitations',
            i18n_domain='PleiadesEntity',
        ),
        size=0,
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

class Work(BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IWork)

    _at_rename_after_creation = True

    schema = Work_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('rangesText')
    def rangesText(self):
        return ' '.join([c['range'] for c in self.getReferenceCitations()])

    security.declarePublic('getCitationTypes')
    def getCitationTypes(self):
        return dict(ReferenceCitation.schema["type"].vocabulary)

    security.declarePublic('getSortedReferenceCitations')
    def getSortedReferenceCitations(self):
        vocab = self.getCitationTypes()
        refs = {}
        # Access once to prime it. TODO: WTF?
        self.getReferenceCitations()
        for c in self.getReferenceCitations():
            label = vocab[c.get('type', "seeFurther")]
            if label not in refs.keys():
                refs[label] = []
            cite = c.copy()
            del cite['type']
            refs[label].append(cite.items())
        return sorted(refs.items())

# end of class Work

##code-section module-footer #fill in your manual code here
##/code-section module-footer



