# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2009 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
# Generator: ArchGenXML Version 2.4.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Sean Gillies <unknown>, Tom Elliott <unknown>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('PleiadesEntity: setuphandlers')
from Products.PleiadesEntity.config import PROJECTNAME
from Products.PleiadesEntity.config import DEPENDENCIES
import os
from config import product_globals
from Globals import package_home
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES
TYPES_TO_VERSION = (
    'Feature',
    'Location',
    'Name',
    'Place',
    'PositionalAccuracy',
    'PrimaryReference',
    'SecondaryReference'
    )
##/code-section HEAD

def isNotPleiadesEntityProfile(context):
    return context.readDataFile("PleiadesEntity_marker.txt") is None

def installVocabularies(context):
    """creates/imports the atvm vocabs."""
    if isNotPleiadesEntityProfile(context): return 
    site = context.getSite()
    # Create vocabularies in vocabulary lib
    atvm = getToolByName(site, ATVOCABULARYTOOL)
    vocabmap = {'name-accuracy': ('VdexVocabulary', 'VdexTerm'),
         'association-certainty': ('VdexVocabulary', 'VdexTerm'),
         'place-types': ('SimpleVocabulary', 'SimpleVocabularyTerm'),
         'attestation-confidence': ('VdexVocabulary', 'VdexTerm'),
         'time-periods': ('VdexVocabulary', 'VdexTerm'),
         'name-completeness': ('VdexVocabulary', 'VdexTerm'),
         'ancient-name-languages': ('VdexVocabulary', 'VdexTerm'),
         'name-types': ('VdexVocabulary', 'VdexTerm'),
        }
    for vocabname in vocabmap.keys():
        if not vocabname in atvm.contentIds():
            atvm.invokeFactory(vocabmap[vocabname][0], vocabname)

        if len(atvm[vocabname].contentIds()) < 1:
            if vocabmap[vocabname][0] == "VdexVocabulary":
                vdexpath = os.path.join(
                    package_home(product_globals), 'data', '%s.vdex' % vocabname)
                if not (os.path.exists(vdexpath) and os.path.isfile(vdexpath)):
                    logger.warn('No VDEX import file provided at %s.' % vdexpath)
                    continue
                try:
                    #read data
                    f = open(vdexpath, 'r')
                    data = f.read()
                    f.close()
                except:
                    logger.warn("Problems while reading VDEX import file "+\
                                "provided at %s." % vdexpath)
                    continue
                # this might take some time!
                atvm[vocabname].importXMLBinding(data)
            else:
                pass



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotPleiadesEntityProfile(context): return 
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotPleiadesEntityProfile(context): return
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'PleiadesEntity': # avoid infinite recursions
        return
    site = context.getSite()



##code-section FOOT
def setVersionedTypes(context):
    portal_repository = getToolByName(context.getSite(), 'portal_repository')
    versionable_types = list(portal_repository.getVersionableContentTypes())
    for type_id in TYPES_TO_VERSION:
        if type_id not in versionable_types:
            # use append() to make sure we don't overwrite any
            # content-types which may already be under version control
            versionable_types.append(type_id)
            # Add default versioning policies to the versioned type
            for policy_id in DEFAULT_POLICIES:
                portal_repository.addPolicyForContentType(type_id, policy_id)
    portal_repository.setVersionableContentTypes(versionable_types)
##/code-section FOOT
