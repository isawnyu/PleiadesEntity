# ===========================================================================
# Copyright (c) 2006 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.

# Generator: ArchGenXML Version 1.5.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# About Pleiades
# --------------
#
# Pleiades is an international research network and associated web portal and
# content management system devoted to the study of ancient geography. 
#
# See http://icon.stoa.org/trac/pleiades/wiki.
#
# Funding for the creation of this software was provided by a grant from the 
# U.S. National Endowment for the Humanities (http://www.neh.gov).
# ===========================================================================

__author__ = """Sean Gillies <unknown>, Tom Elliott <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.GeographicEntityLite.config import *

##code-section module-header #fill in your manual code here
from Products.Archetypes.utils import DisplayList
from Products.PloneLanguageTool import LanguageTool
from Products.CMFCore.utils import getToolByName
import sys,logging
import operator
import transaction
##/code-section module-header

schema = Schema((

    StringField(
        name='nameLanguage',
        widget=StringWidget(
            label="Language and Writing System of Attested Name",
            label_msgid='GeographicEntityLite_label_nameLanguage',
            i18n_domain='GeographicEntityLite',
        )
    ),

    LinesField(
        name='timePeriods',
        widget=LinesWidget(
            label="Time Periods",
            label_msgid='GeographicEntityLite_label_timePeriods',
            i18n_domain='GeographicEntityLite',
        )
    ),

    LinesField(
        name='primaryReferences',
        widget=LinesWidget(
            label="Primary References",
            label_msgid='GeographicEntityLite_label_primaryReferences',
            i18n_domain='GeographicEntityLite',
        )
    ),

    LinesField(
        name='secondaryReferences',
        widget=LinesWidget(
            label="Secondary References",
            label_msgid='GeographicEntityLite_label_secondaryReferences',
            i18n_domain='GeographicEntityLite',
        )
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

GeographicNameLite_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class GeographicNameLite(BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Geographic Name (Lite)'

    meta_type = 'GeographicNameLite'
    portal_type = 'GeographicNameLite'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    content_icon = 'geonlite_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Geographic Name (Lite)"
    typeDescMsgId = 'description_edit_geographicnamelite'

    _at_rename_after_creation = False

    schema = GeographicNameLite_schema

    ##code-section class-header #fill in your manual code here
    schema['title'].widget.label = 'Name as Attested'
    ##/code-section class-header

    # Methods

    # Manually created methods

    security.declarePrivate('at_post_edit_script')
    def at_post_edit_script(self):
        newID = self.cookMyID()
        transaction.savepoint(optimistic=True)
        self.setId(value=newID)

    security.declarePrivate('cookMyID')
    def cookMyID(self):
        rawID = self.title
        cookedID = rawID.replace(' ', '')
        cookedID = cookedID.lower()
        return cookedID.encode('ascii', 'replace')

    security.declarePrivate('at_post_create_script')
    def at_post_create_script(self):
        self.at_post_edit_script()



registerType(GeographicNameLite, PROJECTNAME)
# end of class GeographicNameLite

##code-section module-footer #fill in your manual code here


##/code-section module-footer



