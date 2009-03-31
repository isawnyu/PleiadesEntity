# -*- coding: utf-8 -*-
#
# File: PositionalAccuracy.py
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

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.PleiadesEntity.config import *

# additional imports from tagged value 'import'
from Products.ATBackRef.backref import BackReferenceField, BackReferenceWidget

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
    BackReferenceField(
        name='locations',
        widget=BackReferenceWidget(
            visible={'view': 'visible', 'edit': 'invisible'},
            label="Describes accuracy of location(s)",
            label_msgid='PleiadesEntity_label_locations',
            i18n_domain='PleiadesEntity',
            macro='betterbackrefwidget'
        ),
        multiValued=True,
        relationship="location_accuracy",
    ),

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

registerType(PositionalAccuracy, PROJECTNAME)
# end of class PositionalAccuracy

##code-section module-footer #fill in your manual code here
##/code-section module-footer



