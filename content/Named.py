# -*- coding: utf-8 -*-
#
# File: Named.py
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

# additional imports from tagged value 'import'
from Products.CMFCore import permissions

##code-section module-header #fill in your manual code here
from Products.PleiadesEntity.time import TimePeriodCmp
##/code-section module-header

schema = Schema((

    StringField(
        name='modernLocation',
        widget=StringField._properties['widget'](
            label="Modern location",
            description="Enter the name of a modern location or vicinity of the ancient place",
            label_msgid='PleiadesEntity_label_modernLocation',
            description_msgid='PleiadesEntity_help_modernLocation',
            i18n_domain='PleiadesEntity',
        ),
        description="The modern location or vicinity of the ancient place or feature",
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Named_schema = schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Named(BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.INamed)

    _at_rename_after_creation = True

    schema = Named_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declareProtected(permissions.View, 'get_title')
    def get_title(self):
        """Return a title string derived from contained ancient names.
        """
        try:
            names = self.getNames()
            if names:
                return '/'.join([n.Title() for n in names if n.Title()])
            else:
                return "Unnamed %s" % self.getFeatureType().capitalize()
        except AttributeError:
            return 'Unnamed Place'

    security.declareProtected(permissions.View, 'getNames')
    def getNames(self):
        """
        """
        return [o for o in self.values() if interfaces.IName.providedBy(o)]

# end of class Named

##code-section module-footer #fill in your manual code here
##/code-section module-footer



