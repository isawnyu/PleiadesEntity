# -*- coding: utf-8 -*-
#
# File: PrimaryReference.py
#
# Copyright (c) 2009 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
# Generator: ArchGenXML Version 2.1
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
        name='names',
        widget=BackReferenceWidget(
            visible={'view': 'visible', 'edit': 'invisible'},
            label="Cited by name(s)",
            label_msgid='PleiadesEntity_label_names',
            i18n_domain='PleiadesEntity',
        ),
        multiValued=True,
        relationship="name_reference",
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PrimaryReference_schema = BaseSchema.copy() + \
    getattr(Reference, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PrimaryReference(BaseContent, Reference, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IPrimaryReference)

    meta_type = 'PrimaryReference'
    _at_rename_after_creation = True

    schema = PrimaryReference_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(PrimaryReference, PROJECTNAME)
# end of class PrimaryReference

##code-section module-footer #fill in your manual code here
##/code-section module-footer



