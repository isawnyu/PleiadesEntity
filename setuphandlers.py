# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
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
##/code-section HEAD

def isNotPleiadesEntityProfile(context):
    return context.readDataFile("PleiadesEntity_marker.txt") is None

def installVocabularies(context):
    """creates/imports the atvm vocabs."""
    if isNotPleiadesEntityProfile(context): return 
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'PleiadesEntity': # avoid infinite recursions
        return
    site = context.getSite()
    # Create vocabularies in vocabulary lib
    atvm = getToolByName(site, ATVOCABULARYTOOL)
    vocabmap = {'name-accuracy': ('VdexVocabulary', 'VdexTerm'),
         'association-certainty': ('VdexVocabulary', 'VdexTerm'),
         'place-types': ('VdexVocabulary', 'VdexTerm'),
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
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'PleiadesEntity': # avoid infinite recursions
        return
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
##/code-section FOOT
