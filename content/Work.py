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
            description="Reference work and citation range",
            multiValued=True,
        ),

        widget=EnhancedArrayWidget(
            label="References",
            description="Add or remove references",
            macro="pleiadescitationrefwidget",
            label_msgid='PleiadesEntity_label_array:referenceCitations',
            description_msgid='PleiadesEntity_help_array:referenceCitations',
            i18n_domain='PleiadesEntity',
        ),
        size=0,
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

# end of class Work

##code-section module-footer #fill in your manual code here
##/code-section module-footer



