# -*- coding: utf-8 -*-
#
# File: PleiadesEntity.py
#
# Copyright (c) 2009 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
# Generator: ArchGenXML Version 2.4.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Sean Gillies <unknown>, Tom Elliott <unknown>"""
__docformat__ = 'plaintext'


# There are three ways to inject custom code here:
#
#   - To set global configuration variables, create a file AppConfig.py.
#       This will be imported in config.py, which in turn is imported in
#       each generated class and in this file.
#   - To perform custom initialisation after types have been registered,
#       use the protected code section at the bottom of initialize().

from AccessControl import allow_class, allow_module
from config import *
from Products.Archetypes.atapi import process_types
from Products.Archetypes import listTypes
from Products.CMFCore import DirectoryView
from Products.CMFCore import utils as cmfutils
from Products.Archetypes.atapi import process_types
from Products.Archetypes.atapi import BaseSchema
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.ATContentTypes.content.event import ATEventSchema
from Products.ATContentTypes.content.newsitem import ATNewsItemSchema
from Products.ATContentTypes.content.link import ATLinkSchema
from Products.ATContentTypes.content.image import ATImageSchema
from Products.ATContentTypes.content.file import ATFileSchema
from Products.ATContentTypes.content.topic import ATTopicSchema

# Patch AT schemas to hide DC Location field
BaseSchema['location'].widget.visible = {
    'edit': 'invisible', 'view': 'invisible'
}
ATContentTypeSchema['location'].widget = \
    ATFolderSchema['location'].widget = \
    ATDocumentSchema['location'].widget = \
    ATEventSchema['location'].widget = \
    ATNewsItemSchema['location'].widget = \
    ATLinkSchema['location'].widget = \
    ATImageSchema['location'].widget = \
    ATFileSchema['location'].widget = \
    ATTopicSchema['location'].widget = BaseSchema['location'].widget

DirectoryView.registerDirectory('skins', product_globals)

allow_module("Products.PleiadesEntity.content.interfaces")
from Products.PleiadesEntity.content.interfaces import IPlace
allow_class(IPlace)


def initialize(context):
    """initialize product (called by zope)"""

    # imports packages and types for registration
    import content

    # Initialize portal content
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types=all_content_types,
        permission=DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors=all_constructors,
        fti=all_ftis,
        ).initialize(context)

    # Give it some extra permissions to control them on a per class limit
    for i in range(0, len(all_content_types)):
        klassname = all_content_types[i].__name__
        if klassname not in ADD_CONTENT_PERMISSIONS:
            continue

        context.registerClass(
            meta_type=all_ftis[i]['meta_type'],
            constructors=(all_constructors[i],),
            permission=ADD_CONTENT_PERMISSIONS[klassname])
