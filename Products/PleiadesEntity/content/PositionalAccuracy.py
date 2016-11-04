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

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.ATBackRef.backref import BackReferenceField, BackReferenceWidget
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.PleiadesEntity.config import PROJECTNAME
from zope.interface import implements
import interfaces

schema = atapi.Schema((

    atapi.FloatField(
        name='value',
        widget=atapi.FloatField._properties['widget'](
            label="Positional accuracy",
            description="Enter the accuracy, in meters, of location or position",
            label_msgid='PleiadesEntity_label_value',
            description_msgid='PleiadesEntity_help_value',
            i18n_domain='PleiadesEntity',
        ),
        description="Positional accuracy value in meters",
    ),
    atapi.FileField(
        name='source',
        widget=atapi.FileField._properties['widget'](
            description="Attach feature source file",
            label="Feature source file",
            label_msgid='PleiadesEntity_label_source',
            description_msgid='PleiadesEntity_help_source',
            i18n_domain='PleiadesEntity',
        ),
        storage=atapi.AttributeStorage(),
        description="XML source of features",
    ),
    BackReferenceField(
        name='backrefs',
        widget=BackReferenceWidget(
            visible="{'view': 'visible', 'edit': 'invisible'}",
            macro="betterbackrefwidget",
            label=u'Referenced By',
            hide_inaccessible=True,
        ),
        multiValued=True,
        relationship='location_accuracy',
    ),
))

PositionalAccuracy_schema = ATDocumentSchema.copy() + \
    schema.copy()


class PositionalAccuracy(ATDocument):
    """A description of positional accuracy of a geographic data source.
    """
    security = ClassSecurityInfo()

    implements(interfaces.IPositionalAccuracy)

    meta_type = 'PositionalAccuracy'
    _at_rename_after_creation = True

    schema = PositionalAccuracy_schema

    schema["presentation"].widget.visible = {
        "edit": "invisible", "view": "invisible"}
    schema["tableContents"].widget.visible = {
        "edit": "invisible", "view": "invisible"}


atapi.registerType(PositionalAccuracy, PROJECTNAME)
