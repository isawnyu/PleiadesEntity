# -*- coding: utf-8 -*-
#
# File: Place.py
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
from Products.PleiadesEntity.config import *

##code-section module-header #fill in your manual code here
from Products.CMFCore import permissions
##/code-section module-header

schema = Schema((

    StringField(
        name='modernLocation',
        widget=StringField._properties['widget'](
            label="Modern Location",
            description="The modern location or vicinity of the ancient place",
            label_msgid='PleiadesEntity_label_modernLocation',
            description_msgid='PleiadesEntity_help_modernLocation',
            i18n_domain='PleiadesEntity',
        ),
    ),
    TextField(
        name='content',
        widget=RichWidget(
            label="Content",
            description="About the place",
            label_msgid='PleiadesEntity_label_content',
            description_msgid='PleiadesEntity_help_content',
            i18n_domain='PleiadesEntity',
        ),
    ),
    ReferenceField(
        name='features',
        widget=ReferenceBrowserWidget(
            label='Features',
            label_msgid='PleiadesEntity_label_features',
            i18n_domain='PleiadesEntity',
        ),
        allowed_types=('Feature',),
        multiValued=1,
        relationship='hasFeature',
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Place_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Place(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IPlace)

    meta_type = 'Place'
    _at_rename_after_creation = False

    schema = Place_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('Title')
    def Title(self):
        """
        """
        titles = []
        types = []
        for o in self.getFeatures():
            try:
                name = o.getRefs('hasName')[0]
                titles.append(name.Title())
                types.append(name.getNameType())
            except:
                pass
        if len(titles) == 0:
            return 'Unnamed Place'
        else:
            return '/'.join(titles)

    security.declarePublic('getTimePeriods')
    def getTimePeriods(self):
        """
        """
        result = []
        for o in self.getFeatures():
            for t in o.getTimePeriods():
                if t not in result:
                    result.append(t)
        return result

    security.declarePublic('getPlaceType')
    def getPlaceType(self):
        """
        """
        result = []
        for o in self.getFeatures():
            t = o.getFeatureType()
            if t not in result:
                result.append(t)
        return result

    # Manually created methods

    security.declareProtected(permissions.View, 'getFeatures')
    def getFeatures(self):
         for o in self.getRefs('hasFeature'):
            if interfaces.IFeature.providedBy(o):
                yield o



registerType(Place, PROJECTNAME)
# end of class Place

##code-section module-footer #fill in your manual code here
##/code-section module-footer



