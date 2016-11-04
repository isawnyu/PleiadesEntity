# -*- coding: utf-8 -*-
#
# File: PositionalAccuracy.py
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

from Products.CMFCore.utils import getToolByName

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.PleiadesEntity.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    FloatField(
        name='value',
        widget=FloatField._properties['widget'](
            label="Positional accuracy",
            description="Enter the accuracy, in meters, of location or position",
            label_msgid='PleiadesEntity_label_value',
            description_msgid='PleiadesEntity_help_value',
            i18n_domain='PleiadesEntity',
        ),
        description="Positional accuracy value in meters",
    ),
    FileField(
        name='source',
        widget=FileField._properties['widget'](
            description="Attach feature source file",
            label="Feature source file",
            label_msgid='PleiadesEntity_label_source',
            description_msgid='PleiadesEntity_help_source',
            i18n_domain='PleiadesEntity',
        ),
        storage=AttributeStorage(),
        description="XML source of features",
    ),
    ComputedField(
        name='refCount',
        expression='context.countReferences()',
        read_permission='Manage portal',
        widget=ComputedWidget(
            label='Reference count',
            modes=('view',),
        ),
    )
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PositionalAccuracy_schema = ATDocumentSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PositionalAccuracy(ATDocument):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IPositionalAccuracy)

    meta_type = 'PositionalAccuracy'
    _at_rename_after_creation = True

    schema = PositionalAccuracy_schema

    ##code-section class-header #fill in your manual code here
    schema["presentation"].widget.visible = {"edit": "invisible", "view": "invisible"}
    schema["tableContents"].widget.visible = {"edit": "invisible", "view": "invisible"}
    ##/code-section class-header

    # Methods

    def countReferences(self):
        tool = getToolByName(self, 'reference_catalog')
        brains = tool.getBackReferences(
            self, 'location_accuracy', objects=False)
        return len(brains)


registerType(PositionalAccuracy, PROJECTNAME)
# end of class PositionalAccuracy

##code-section module-footer #fill in your manual code here
##/code-section module-footer



