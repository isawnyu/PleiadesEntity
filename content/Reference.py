# -*- coding: utf-8 -*-
#
# File: Reference.py
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

from Products.PleiadesEntity.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

copied_fields = {}
copied_fields['title'] = BaseSchema['title'].copy()
copied_fields['title'].widget.label = "Citation"
schema = Schema((

    copied_fields['title'],

    StringField(
        name='item',
        widget=StringField._properties['widget'](
            macro="url_widget",
            label='Item',
            label_msgid='PleiadesEntity_label_item',
            i18n_domain='PleiadesEntity',
        ),
    ),
    StringField(
        name='range',
        widget=StringField._properties['widget'](
            label="Citation range",
            label_msgid='PleiadesEntity_label_range',
            i18n_domain='PleiadesEntity',
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Reference_schema = schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Reference(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IReference)

    _at_rename_after_creation = True

    schema = Reference_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

# end of class Reference

##code-section module-footer #fill in your manual code here
##/code-section module-footer



