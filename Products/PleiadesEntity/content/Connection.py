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
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
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
        ),
        description="Connection to another place",
        multiValued=False,
        relationship='connection',
        allowed_types=('Place',),
        allow_browse=False,
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
        widget=atapi.SelectionWidget(
            label="Association Certainty",
            description="Select level of certainty in association between location and place",
            label_msgid='PleiadesEntity_label_associationCertainty',
            description_msgid='PleiadesEntity_help_associationCertainty',
            i18n_domain='PleiadesEntity',
        ),
        description="Level of certainty in association between location and place",
        vocabulary=NamedVocabulary("""association-certainty"""),
        default="certain",
        enforceVocabulary=1,
    ),

))

Connection_schema = ATDocumentSchema.copy() + schema.copy() + \
    getattr(Temporal, 'schema', atapi.Schema(())).copy() + \
    getattr(Work, 'schema', atapi.Schema(())).copy()
schema = Connection_schema

off = {"edit": "invisible", "view": "invisible"}

schema["title"].required = 0
schema["title"].widget.visible = off
schema["description"].widget.visible = off
schema["text"].widget.visible = off

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

atapi.registerType(Connection, PROJECTNAME)
