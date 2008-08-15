# -*- coding: utf-8 -*-
#
# File: Feature.py
#
# Copyright (c) 2008 by Ancient World Mapping Center, University of North
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
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.PleiadesEntity.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='featureType',
        widget=SelectionWidget(
            label="Feature type",
            label_msgid='PleiadesEntity_label_featureType',
            i18n_domain='PleiadesEntity',
        ),
        vocabulary=NamedVocabulary("""place-types"""),
        default="unknown",
        enforceVocabulary=1,
    ),
    StringField(
        name='associationCertainty',
        widget=SelectionWidget(
            label="Certainty of association",
            description="Certainty of association between locations and names",
            label_msgid='PleiadesEntity_label_associationCertainty',
            description_msgid='PleiadesEntity_help_associationCertainty',
            i18n_domain='PleiadesEntity',
        ),
        vocabulary=NamedVocabulary("""association-certainty"""),
        enforceVocabulary=1,
    ),
    ReferenceField(
        name='locations',
        widget=ReferenceBrowserWidget(
            label='Locations',
            label_msgid='PleiadesEntity_label_locations',
            i18n_domain='PleiadesEntity',
        ),
        allowed_types=('Location',),
        multiValued=1,
        relationship='hasLocation',
    ),
    ReferenceField(
        name='names',
        widget=ReferenceBrowserWidget(
            label='Names',
            label_msgid='PleiadesEntity_label_names',
            i18n_domain='PleiadesEntity',
        ),
        allowed_types=('Name',),
        multiValued=1,
        relationship='hasName',
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Feature_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Feature(BaseFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IFeature)

    meta_type = 'Feature'
    _at_rename_after_creation = False

    schema = Feature_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('get_title')
    def get_title(self):
        """Return a title string derived from the ancient names to which
        this place refers.
        """
        # Dodge a reference_catalog quirk
        try:
            names = self.getRefs('hasName')
            if names:
                return '/'.join([n.Title() for n in names])
            else:
                return "Unnamed %s" % self.getFeatureType().capitalize()
        except AttributeError:
            return 'Unnamed Place'

    security.declarePublic('Title')
    def Title(self):
        """
        """
        return self.get_title()

    security.declarePublic('getTimePeriods')
    def getTimePeriods(self):
        """
        """
        names = self.getRefs('hasName')
        locations = self.getRefs('hasLocation')
        periods = []
        for name in names:
            periods.extend(name.getTimePeriods())
        for location in locations:
            periods.extend(location.getTimePeriods())
        result = []
        for p in periods:
            if p not in result:
                result.append(p)
        return result


registerType(Feature, PROJECTNAME)
# end of class Feature

##code-section module-footer #fill in your manual code here
##/code-section module-footer



