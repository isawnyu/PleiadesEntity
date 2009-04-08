# -*- coding: utf-8 -*-
#
# File: SecondaryReference.py
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
from Products.PleiadesEntity.content.Reference import Reference
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.PleiadesEntity.config import *

# additional imports from tagged value 'import'
from Products.ATBackRef.backref import BackReferenceField, BackReferenceWidget

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    BackReferenceField(
        name='items',
        widget=BackReferenceWidget(
            visible="{'view': 'visible', 'edit': 'invisible'}",
            label="Cited by item(s)",
            macro="betterbackrefwidget",
            label_msgid='PleiadesEntity_label_items',
            i18n_domain='PleiadesEntity',
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

SecondaryReference_schema = BaseSchema.copy() + \
    getattr(Reference, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class SecondaryReference(BaseContent, Reference, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.ISecondaryReference)

    meta_type = 'SecondaryReference'
    _at_rename_after_creation = True

    schema = SecondaryReference_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(SecondaryReference, PROJECTNAME)
# end of class SecondaryReference

##code-section module-footer #fill in your manual code here
##/code-section module-footer



