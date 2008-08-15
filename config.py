# -*- coding: utf-8 -*-
#
# File: PleiadesEntity.py
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


# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. The items in there
# will be included (by importing) in this file if found.

from Products.CMFCore.permissions import setDefaultRoles
##code-section config-head #fill in your manual code here
##/code-section config-head


PROJECTNAME = "PleiadesEntity"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
ADD_CONTENT_PERMISSIONS = {
    'Name': 'PleiadesEntity: Add Name',
    'Location': 'PleiadesEntity: Add Location',
    'TemporalAttestation': 'PleiadesEntity: Add TemporalAttestation',
    'Reference': 'PleiadesEntity: Add Reference',
    'SecondaryReference': 'PleiadesEntity: Add SecondaryReference',
    'PrimaryReference': 'PleiadesEntity: Add PrimaryReference',
    'Feature': 'PleiadesEntity: Add Feature',
    'NameContainer': 'PleiadesEntity: Add NameContainer',
    'LocationContainer': 'PleiadesEntity: Add LocationContainer',
    'PlaceContainer': 'PleiadesEntity: Add PlaceContainer',
    'Place': 'PleiadesEntity: Add Place',
    'FeatureContainer': 'PleiadesEntity: Add FeatureContainer',
}

setDefaultRoles('PleiadesEntity: Add Name', ('Manager','Owner'))
setDefaultRoles('PleiadesEntity: Add Location', ('Manager','Owner'))
setDefaultRoles('PleiadesEntity: Add TemporalAttestation', ('Manager','Owner'))
setDefaultRoles('PleiadesEntity: Add Reference', ('Manager','Owner'))
setDefaultRoles('PleiadesEntity: Add SecondaryReference', ('Manager','Owner'))
setDefaultRoles('PleiadesEntity: Add PrimaryReference', ('Manager','Owner'))
setDefaultRoles('PleiadesEntity: Add Feature', ('Manager','Owner'))
setDefaultRoles('PleiadesEntity: Add NameContainer', ('Manager','Owner'))
setDefaultRoles('PleiadesEntity: Add LocationContainer', ('Manager','Owner'))
setDefaultRoles('PleiadesEntity: Add PlaceContainer', ('Manager','Owner'))
setDefaultRoles('PleiadesEntity: Add Place', ('Manager','Owner'))
setDefaultRoles('PleiadesEntity: Add FeatureContainer', ('Manager','Owner'))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

##code-section config-bottom #fill in your manual code here
##/code-section config-bottom


# Load custom configuration not managed by archgenxml
try:
    from Products.PleiadesEntity.AppConfig import *
except ImportError:
    pass
