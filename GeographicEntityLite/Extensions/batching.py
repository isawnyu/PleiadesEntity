# ===========================================================================
# Copyright (C) 2006 Ancient World Mapping Center
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

#from Products.GeographicEntityLite.config import PROJECTNAME
#from Products.GeographicEntityLite.Extensions.xmlutil import getXMLDOM, getXMLText
#from Products.GeographicEntityLite.Extensions.creationutil import setupContentItem

import glob
import sys
import re

from Products.GeographicEntityLite.Extensions.xmlutil import *
from Products.GeographicEntityLite.cooking import *

def loaden(self, sourcedir):
    for xml in glob.glob("%s/*.xml" % sourcedir):
        load_entity(self, xml)
        
def load_entity(plonefolder, source):
    """Create a new GeographicEntityLite in plonefolder and populate it with
    the data found in the xml file at sourcepath."""
    
    # instantiation of geoEntity attempts to load the file via the path source
    ge = geoEntity(source)
    
    # create the corresponding entity instance in plone and set its fields
    enID = plonefolder.invokeFactory('GeographicEntityLite', id=ge.identifier)
    
    en = getattr(plonefolder, enID)
    
    en.setTitle(ge.identifier)
    newEnID = enID
    #newEnID = setIDFromTitle(en)
    
    en.setGeoEntityType(ge.classifications['geoEntityType'])
    
    en.setModernLocation(ge.modernLocation)
    
    en.setTimePeriods(ge.timePeriods)
    
    en.setSecondaryReferences(ge.secondaryReferences)
    
    en.setDescription('No description')
    
    coords = ge.spatialLocations[0][1].replace(',', ' ')
    values = [v for v in coords.split()]
    if len(values) == 2:
        values.append('0.0')
    en.setSpatialCoordinates(' '.join(values))
    
    # add any names as children of the entity
    for i, name in enumerate(ge.names):
        nameID = en.invokeFactory('GeographicNameLite', id=newEnID + '-n' + `i+1`)
        en_name = getattr(en, nameID)
        en_name.setTitle(nameID)
        en_name.setDescription('No description')
        en_name.setNameAttested(name.nameString)
        en_name.setNameTransliterated(name.nameStringTransliterated)
        en_name.setNameLanguage(name.language)
        en_name.setTimePeriods(name.timePeriods)
        en_name.setPrimaryReferences(name.primaryReferences)
        en_name.setSecondaryReferences(name.secondaryReferences)
        # classifications!
        
class geoName:
    
    def __init__(self, sourcenode):
        self.nameString = u''
        self.nameStringTransliterated = u''
        self.language = ''
        self.timePeriods = []
        self.primaryReferences = []
        self.secondaryReferences = []
        self.classifications = {}
        
        self.parse_Node(sourcenode)
        
    def parse_Node(self, node):
        parseMethod = getattr(self, "parse_%s" % node.__class__.__name__)
        parseMethod(node)
        
    def parse_Document(self, node):
        self.parse_Node(node.documentElement)
        
    def parse_Text(self, node): 
        pass
        
    def parse_Element(self, node): 
        handlerMethod = getattr(self, "hdl_%s" % node.tagName)
        handlerMethod(node)
        
    def parse_Comment(self, node):
        pass
        
    def hdl_name(self, node):
        for childnode in node.childNodes:
            self.parse_Node(childnode)
            
    def hdl_nameString(self, node):
        self.nameString = getXMLText([node])
        
    def hdl_nameStringTransliterated(self, node):
        self.nameStringTransliterated = getXMLText([node])
        
    def hdl_classificationSection(self, node):
        thesaurus =  getXMLText(node.getElementsByTagName('classificationScheme')[0].getElementsByTagName('schemeName'))
        term = getXMLText(node.getElementsByTagName('classificationTerm'))
        self.classifications[thesaurus] = term
        
    def hdl_timePeriod(self, node):
        period_name = getXMLText(node.getElementsByTagName('timePeriodName'))
        self.timePeriods.append(period_name)
        
    def hdl_secondaryReferences(self, node):
        for childnode in node.childNodes:
            if childnode.nodeType == node.ELEMENT_NODE:
                if childnode.tagName == 'tei:bibl':
                    reference = getXMLText([childnode])
                    self.secondaryReferences.append(reference)
            
        
class geoEntity:
    
    def __init__(self, source):
        self.identifier = u''
        self.modernLocation = u''
        self.timePeriods = []
        self.spatialLocations = []
        self.secondaryReferences = []
        self.classifications = {}
        self.names = []
        
        self.loadSource(source)
        
    def _load(self, source):
        """load xml source for entity"""
        xmldoc = getXMLDOM(source)
        self.parse_Document(xmldoc)
        
    def loadSource(self, source):
        source = self._load(source)
        
    def parse_Node(self, node):
        parseMethod = getattr(self, "parse_%s" % node.__class__.__name__)
        parseMethod(node)
        
    def parse_Document(self, node):
        self.parse_Node(node.documentElement)
        
    def parse_Text(self, node): 
        pass
        
    def parse_Element(self, node): 
        handlerMethod = getattr(self, "hdl_%s" % node.tagName)
        handlerMethod(node)
        
        
    def parse_Comment(self, node):
        pass
        
        
    def hdl_geoEntity(self, node):
        for childnode in node.childNodes:
            self.parse_Node(childnode)
        
    def hdl_ID(self, node):
        "Handle an identifier tag"
        self.identifier = getXMLText([node])
        
    def hdl_modernLocation(self, node):
        location = getXMLText(node.childNodes)
        self.modernLocation = location
        
    def hdl_timePeriod(self, node):
        period_name = getXMLText(node.getElementsByTagName('timePeriodName'))
        self.timePeriods.append(period_name)
        
    def hdl_classificationSection(self, node):
        thesaurus =  getXMLText(node.getElementsByTagName('classificationScheme')[0].getElementsByTagName('schemeName'))
        term = getXMLText(node.getElementsByTagName('classificationTerm'))
        self.classifications[thesaurus] = term
        
    def hdl_name(self, node):
        self.names.append(geoName(node))
    
    def hdl_spatialLocation(self, node):
        for childnode in node.childNodes:
            if childnode.nodeType == node.ELEMENT_NODE:
                self.spatialLocations.append((childnode.tagName, getXMLText(childnode.childNodes)))
    
    def hdl_secondaryReferences(self, node):
        for childnode in node.childNodes:
            if childnode.nodeType == node.ELEMENT_NODE:
                if childnode.tagName == 'tei:bibl':
                    reference = getXMLText([childnode])
                    self.secondaryReferences.append(reference)
            
    
