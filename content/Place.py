# -*- coding: utf-8 -*-
#
# File: Place.py
#
# Copyright (c) 2008 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
# Generator: ArchGenXML Version 2.0
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
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Place_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Place(BaseFolder, BrowserDefaultMixin):
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
        try:
            associations = self.listFolderContents()
            nametitles = []
            nametypes = []
            for a in associations:
                try:
                    name = a.getRefs('hasName')[0]              # there can only be one name per association
                    nametitles.append(name.Title())
                    nametypes.append(name.getNameType())
                except:
                    pass
            title = '/'.join([title for i, title in enumerate(nametitles) if nametypes[i] == 'geographic' and not title.startswith('Unnamed')])
            if title == '':
                '/'.join([title for title in nametitles if not title.startswith('Unnamed')])
            return title
        except AttributeError:
            return 'Unnamed Place'

    security.declarePublic('getTimePeriods')
    def getTimePeriods(self):
        """
        """
        result = []
        for a in self.listFolderContents():
            for p in a.getTimePeriods():
                if p not in result:
                    result.append(p)
        return result

    security.declarePublic('getPlaceType')
    def getPlaceType(self):
        """
        """
        result = []
        for a in self.listFolderContents():
            if a.getPlaceType() not in result:
                result.append(a.getPlaceType())
        return result


registerType(Place, PROJECTNAME)
# end of class Place

##code-section module-footer #fill in your manual code here
##/code-section module-footer



