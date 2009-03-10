# -*- coding: utf-8 -*-
#
# File: Work.py
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

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget
from Products.PleiadesEntity.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    ReferenceField(
        name='secondaryReferences',
        widget=ReferenceBrowserWidget(
            startup_directory="/references",
            label="Secondary references",
            description="Browse and select secondary references",
            label_msgid='PleiadesEntity_label_secondaryReferences',
            description_msgid='PleiadesEntity_help_secondaryReferences',
            i18n_domain='PleiadesEntity',
        ),
        multiValued=1,
        relationship="work_reference",
        allowed_types=('SecondaryReference',),
        allow_browse=1,
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

# end of class Work

##code-section module-footer #fill in your manual code here
##/code-section module-footer



