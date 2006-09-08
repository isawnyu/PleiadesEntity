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

from Products.GeographicEntityLite.Extensions.xmlutil import *
#from creationutil import *

def loaden(self, sourcedir):
    for xml in glob.glob("%s/*.xml" % sourcedir):
        load_entity(self, xml)
        
def load_entity(plonefolder, source):
    """Create a new GeographicEntityLite in plonefolder and populate it with
    the data found in the xml file at sourcepath."""
    ge = geoEntity(source)
    id = plonefolder.invokeFactory('GeographicEntityLite', id=ge.identifier)
    en = getattr(plonefolder, id)
    en.setModernLocation(ge.modernLocation)
    en.setTimePeriods(ge.timePeriods)
    en.setSecondaryReferences(ge.secondaryReferences)
    coords = ge.spatialLocations[0][1]
    coords = coords.replace(',', ' ')
    en.setSpatialCoordinates(coords)


class geoEntity:
    
    def __init__(self, source):
        self.identifier = u''
        self.modernLocation = u''
        self.timePeriods = []
        self.spatialLocations = []
        self.secondaryReferences = []
        self.classifications = {}
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
        
    def hdl_spatialLocation(self, node):
        for childnode in node.childNodes:
            if childnode.nodeType == node.ELEMENT_NODE:
                self.spatialLocations.append((childnode.tagName, getXMLText(childnode.childNodes)))
    
    def hdl_secondaryReferences(self, node):
        reference = getXMLText(node.getElementsByTagName('tei:bibl'))
        self.secondaryReferences.append(reference)
        
    
