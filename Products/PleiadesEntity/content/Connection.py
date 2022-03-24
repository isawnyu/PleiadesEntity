# -*- coding: utf-8 -*-
#
# File: Connection.py
#
# Copyright (c) 2009 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
# Generator: ArchGenXML Version 2.4.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
from AccessControl import ClassSecurityInfo
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from pleiades.vocabularies.widget import FilteredSelectionWidget
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.CMFCore import permissions
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.PleiadesEntity.content.Temporal import Temporal
from Products.PleiadesEntity.content.Work import Work
from zope.interface import implements
from ..config import PROJECTNAME
import interfaces


schema = atapi.Schema((

    atapi.ReferenceField(
        name='connection',
        widget=ReferenceBrowserWidget(
            startup_directory="/places",
            label="Makes a connection with",
            description=u'Establishes a connection to another place.',
            label_msgid='PleiadesEntity_label_connections',
            i18n_domain='PleiadesEntity',
            allow_browse=False,
        ),
        description="Connection to another place",
        multiValued=False,
        relationship='connection',
        allowed_types=('Place',),
        required=True,
    ),

    atapi.StringField(
        name='relationshipType',
        widget=FilteredSelectionWidget(
            format="select",
            label="Connection type",
            description="Select type of connection being established",
            label_msgid='PleiadesEntity_label_relationshipType',
            description_msgid='PleiadesEntity_help_relationshipType',
            i18n_domain='PleiadesEntity',
        ),
        description="Type of connection established",
        vocabulary_factory='pleiades.vocabularies.relationship_types',
        default="connection",
        enforceVocabulary=1,
    ),

    atapi.StringField(
        name='associationCertainty',
        widget=FilteredSelectionWidget(
            label="Association Certainty",
            description="Select level of certainty in association between location and place",
            label_msgid='PleiadesEntity_label_associationCertainty',
            description_msgid='PleiadesEntity_help_associationCertainty',
            i18n_domain='PleiadesEntity',
            format='radio',
        ),
        description="Level of certainty in association between location and place",
        vocabulary_factory='pleiades.vocabularies.association_certainty',
        default="certain",
        enforceVocabulary=1,
    ),

    atapi.ComputedField(
        name='temporalConstraints',
        mode="rw",
        expression="'<i>Proleptic Julian years prior to establishment of the Gregorian calendar</i>'",
        edit_accessor='getTemporalConstraints',
        widget=atapi.ComputedWidget(
            label="Temporal Constraints",
            visible={'edit': 'visible',
                     'view': 'visible'},
        ),
    ),

    atapi.IntegerField(
        name='notBefore',
        widget=atapi.IntegerField._properties['widget'](
            label="Not before",
            description="Enter the year as an integer",
            label_msgid='PleiadesEntity_label_notBefore',
            description_msgid='PleiadesEntity_help_notBefore',
            i18n_domain='PleiadesEntity',
        ),
        description="This connection cannot have been before the indicated year",
    ),

    atapi.IntegerField(
        name='notAfter',
        widget=atapi.IntegerField._properties['widget'](
            label="Not after",
            description="Enter the year as an integer",
            label_msgid='PleiadesEntity_label_notAfter',
            description_msgid='PleiadesEntity_help_notAfter',
            i18n_domain='PleiadesEntity',
        ),
        description="This connection cannot have been after the indicated year",
    ),

))

Connection_schema = ATDocumentSchema.copy() + schema.copy() + \
    getattr(Temporal, 'schema', atapi.Schema(())).copy() + \
    getattr(Work, 'schema', atapi.Schema(())).copy()
schema = Connection_schema

off = {"edit": "invisible", "view": "invisible"}

schema["text"].widget.label = 'Details'

schema["effectiveDate"].widget.visible = off
schema["expirationDate"].widget.visible = off
schema["allowDiscussion"].widget.visible = off
schema["excludeFromNav"].widget.visible = off
schema["presentation"].widget.visible = off
schema["tableContents"].widget.visible = off

schemata.finalizeATCTSchema(
    Connection_schema,
    folderish=False,
    moveDiscussion=False
)


class Connection(atapi.BaseContent, Work, Temporal, BrowserDefaultMixin):
    security = ClassSecurityInfo()

    implements(interfaces.IConnection)

    meta_type = 'Connection'
    _at_rename_after_creation = True

    schema = Connection_schema
    schema.moveField('notAfter', after='attestations')
    schema.moveField('notBefore', after='attestations')
    schema.moveField('temporalConstraints', after='attestations')

    # Methods
    def Title(self):
        connection = self.getConnection()
        if connection is not None:
            return connection.Title()
        return '[place not found]'

    security.declareProtected(permissions.View, 'SearchableText')
    def SearchableText(self):
        text = super(Connection, self).SearchableText().strip()
        return text + ' ' + self.Title()

    security.declareProtected(permissions.View, 'post_validate')
    def post_validate(self, REQUEST=None, errors=None):
        not_before = REQUEST.get('notBefore', None)
        not_after = REQUEST.get('notAfter', None)
        if not_before and not_before != 0:
            try:
                not_before = int(not_before)
            except ValueError:
                errors['notBefore'] = "Not before must be an integer"
                not_before = None
        if not_after and not_after != 0:
            try:
                not_after = int(not_after)
            except ValueError:
                errors['notAfter'] = "Not after must be an integer"
                not_after = None
        if not_before == 0:
            errors['notBefore'] = "Not before cannot be zero"
        if not_after == 0:
            errors['notAfter'] = "Not after cannot be zero"
        if not_before and not_after:
            if not_before > not_after:
                errors['notBefore'] = "Not before cannot be higher than Not after"
        temporal_range = self.temporalRange()
        if temporal_range and not_before:
            if not_before < temporal_range[0]:
                errors['notBefore'] = "Not before cannot be before initial year of temporal attestations"
            if not_before > temporal_range[1]:
                errors['notBefore'] = "Not before cannot be after ending year of temporal attestations"
        if temporal_range and not_after:
            if not_after < temporal_range[0]:
                errors['notAfter'] = "Not after cannot be before initial year of temporal attestations"
            if not_after > temporal_range[1]:
                errors['notAfter'] = "Not after cannot be after ending year of temporal attestations"


atapi.registerType(Connection, PROJECTNAME)
