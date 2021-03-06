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

import glob
import sys
import re
from os.path import basename

from Products.PleiadesEntity.Extensions.xmlutil import *
from Products.PleiadesEntity.Extensions.cooking import *

def format_listofstrings(list):
    """convert ['x', 'y', 'z'] to u'x, y, and z'"""
    
    try:
        length = len(list)
    except:
        length = 0
    out = u''
    if length == 0:
        pass
    elif length < 3:
        out = unicode(' and '.join(list))
    else:
        out = unicode(', '.join(list[:-1]))
        out = unicode(' and '.join([out, list[-1]]))
    return out
    
def loaden(self, sourcedir):
    """Attempt to load all XML files in the specified source directory.
    Files which can not be loaded are reported."""
    failures = []
    count = 0
    for xml in glob.glob("%s/*.xml" % sourcedir):
        try:
            load_place(self, xml)
            count += 1
        except:
            failures.append(basename(xml))
    if len(failures) == 0:
        return "Loaded %d of %d files." % (count, count)
    else:
        msg = "Loaded %d of %d files. Failures:\n" % (count, count + len(failures))
        for f in failures:
            msg += "%s\n" % f
        return msg
        
def load_place(plonefolder, source):
    """Create a new Place in plonefolder and populate it with
    the data found in the xml file at sourcepath."""
    
    # instantiation of Place attempts to load the file via the path source
    ge = Place(source)
    
    # create the corresponding place instance in plone and set its fields
    enID = plonefolder.invokeFactory('Place', id=ge.identifier)
    
    en = getattr(plonefolder, enID)
    
    en.setTitle(ge.identifier)
    newEnID = enID
    #newEnID = setIDFromTitle(en)
    
    en.setTitle(ge.identifier)
    en.setPlaceType(ge.classifications['geoEntityType'])
    en.setModernLocation(ge.modernLocation)
    en.setTimePeriods(ge.timePeriods)
    en.setSecondaryReferences(ge.secondaryReferences)
    en.setDescription(ge.description.encode('utf8'))
    en.setContributors(ge.contributors)
    en.setCreators(ge.creators)
    en.setRights(ge.rights)
    
    try:
        coords = ge.spatialLocations[0][1].replace(',', ' ')
    except:
        pass
    else:
        values = [v for v in coords.split()]
        if len(values) == 2:
            values.append('0.0')
        en.setGeometry('Point:[%s,%s]' % (values[1], values[0]) #SpatialCoordinates(' '.join(values))
    
    # add any names as children of the entity
    for i, name in enumerate(ge.names):
        nameID = en.invokeFactory('Name', 
					id="%s-n%d" % (newEnID, i+1))
        en_name = getattr(en, nameID)
        en_name.setTitle(name.nameStringTransliterated)
        #en_name.setIdentifier(nameID)
        en_name.setDescription(name.description.encode('utf8'))
        en_name.setNameAttested(name.nameString)
        en_name.setNameLanguage(name.language)
        en_name.setTimePeriods(name.timePeriods)
        en_name.setPrimaryReferences(name.primaryReferences)
        en_name.setSecondaryReferences(name.secondaryReferences)
        en_name.setNameType(name.classifications['geoNameType'])
        en_name.setCreators(ge.creators)
        en_name.setContributors(ge.contributors)
        en_name.setRights(ge.rights)
        en_name.reindexObject()
       
        
    # rename the entity to reflect the names of its children
    #setGeoTitleFromNames(en)
    
    # refresh appropriate entries in the portal catalog (e.g., the title)
    en.reindexObject()
    
class Name:
    
    def __init__(self, parent, sourcenode):
        self.parent = parent
        self.nameString = u''
        self.nameStringTransliterated = u''
        self.language = ''
        self.timePeriods = []
        self.primaryReferences = []
        self.secondaryReferences = []
        self.classifications = {}
        self.notes = []
        
        self.parse_Node(sourcenode)
        
        self.description = self.calc_Description()
        
    def calc_Description(self):
        entity_type = self.parent.classifications['geoEntityType']
        name_type = self.classifications['geoNameType']
        
        # identification
        identification = u''
        if len(self.nameString) > 0:
            identification = u'(' + self.nameString + u'): '
        if name_type == 'false':
            identification += u'A false name'
        elif entity_type == 'unlocated':
            identification += u'An ancient name for a geographic entity that cannot now be located with certainty'
        else:
            identification += unicode("An ancient %s name for a %s" % (name_type, self.parent.classifications['geoEntityType']))
            
        # periodization
        period_count = len(self.timePeriods)
        if period_count == 0:
            timePeriodsToUse = self.parent.timePeriods
            period_count = len(timePeriodsToUse)
        else:
            timePeriodsToUse = self.timePeriods
        if name_type == 'false':
            periodization = u''
        elif period_count == 0:
            periodization = u', attestation unkown'
        elif period_count == 1:
            periodization = unicode(", attested during the %s period" % timePeriodsToUse[0])
        else:
            periodization \
                = unicode(", attested during the %s periods" \
                % format_listofstrings(timePeriodsToUse))
        
        newDesc = u"%s%s." % (identification, periodization)
        return newDesc
        
    def parse_Node(self, node):
        parseMethod = getattr(self, "parse_%s" % node.__class__.__name__)
        parseMethod(node)
        
    def parse_Document(self, node):
        self.parse_Node(node.documentElement)
        
    def parse_Text(self, node): 
        pass
        
    def parse_Element(self, node): 
        handlerMethod = getattr(self, "hdl_%s" % node.localName)
        handlerMethod(node)
        
    def parse_Comment(self, node):
        pass
        
    def hdl_featureName(self, node):
        for childnode in node.childNodes:
            self.parse_Node(childnode)
            
    def hdl_name(self, node):
        self.nameString = getXMLText([node])
        try:
            langcode = language_vocab[node.attributes.get('xml:lang', '').value]
        except:
            pass
        else:
            self.language = langcode
            
    def hdl_transliteration(self, node):
        self.nameStringTransliterated = getXMLText([node])
        
    def hdl_classificationSection(self, node):
        thesaurus =  getXMLText(node.getElementsByTagName('adlgaz:classificationScheme')[0].getElementsByTagName('adlgaz:schemeName'))
        term = getXMLText(node.getElementsByTagName('adlgaz:classificationTerm'))
        self.classifications[thesaurus] = term
        try:
            for childnode in node.getElementsByTagName('note'):
                self.parse_Node(childnode)
        except:
            pass
        
    def hdl_note(self, node):
        self.notes.append(getXMLText([node]))
        
    def hdl_timePeriod(self, node):
        period_name = getXMLText(node.getElementsByTagName('adlgaz:timePeriodName'))
        self.timePeriods.append(period_name)
        
    def hdl_secondaryReferences(self, node):
        for childnode in node.childNodes:
            if childnode.nodeType == node.ELEMENT_NODE:
                if childnode.tagName == 'tei:bibl':
                    reference = getXMLText([childnode])
                    self.secondaryReferences.append(reference)
            
        
class Place:
    
    def __init__(self, source):
        self.identifier = u''
        self.description = u'No Description'
        self.modernLocation = u''
        self.timePeriods = []
        self.spatialLocations = []
        self.secondaryReferences = []
        self.classifications = {}
        self.names = []
        self.contributors = []
        self.creators = []
        self.rights = ''
        
        self.loadSource(source)
        
        self.description = self.calc_Description()
        
    def _load(self, source):
        """load xml source for entity"""
        xmldoc = getXMLDOM(source)
        self.parse_Document(xmldoc)
        
    def loadSource(self, source):
        source = self._load(source)
        
    def calc_Description(self):
        en_type = self.classifications['geoEntityType']
        
        # identification
        if en_type == 'unlocated':
            identification = u'An ancient geographic entity that cannot now be located with certainty'
        elif en_type == 'false':
            identification = unicode(self.names[0].nameStringTransliterated + u' is a false geographic name')
            if len(self.names[0].notes) > 0:
                identification += u' (' + format_listofstrings(self.names[0].notes) + u')'
        else:
            identification = unicode("An ancient %s" % self.classifications['geoEntityType'])
            
        # periodization
        period_count = len(self.timePeriods)
        if en_type == 'false':
            periodization = u''
        elif period_count == 0:
            periodization = u', attestation unkown'
        elif period_count == 1:
            periodization = unicode(", attested during the %s period" % self.timePeriods[0])
        else:
            periodization \
                = unicode(", attested during the %s periods" \
                % format_listofstrings(self.timePeriods))
        
        #localization
        if self.modernLocation:
            if en_type == 'unlocated':
                localization = unicode(" (approximate modern location: %s)" % self.modernLocation)
            else:
                localization = unicode(" (modern location: %s)" % self.modernLocation)
        else:
            localization = u''
            
        #nomination
        if en_type == 'false':
            nomination = u''
        else:
            namecount = len(self.names)
            if namecount == 0:
                nomination = u'Its ancient name is not known'
            else:
                if namecount == 1:
                    multinames = u''
                else:
                    multinames = u's'
                nomination \
                    = unicode("It was known in antiquity by the name%s: %s" \
                    % (multinames, format_listofstrings([n.nameStringTransliterated for n in self.names])))
        nomination = nomination.strip()
        
        newDesc = u"%s%s%s." % (identification, periodization, localization)
        if len(nomination) > 0:
            newDesc += u' ' + nomination + u'.'
        return newDesc
          
    def parse_Node(self, node):
        parseMethod = getattr(self, "parse_%s" % node.__class__.__name__)
        parseMethod(node)
        
    def parse_Document(self, node):
        self.parse_Node(node.documentElement)
        
    def parse_Text(self, node): 
        pass
        
    def parse_Element(self, node): 
        handlerMethod = getattr(self, "hdl_%s" % node.localName)
        handlerMethod(node)
        
        
    def parse_Comment(self, node):
        pass
        
    def hdl_contributor(self, node):
        self.contributors.append(getXMLText([node]))
        
    def hdl_creator(self, node):
        self.creators.append(getXMLText([node]))
        
    def hdl_geoEntity(self, node):
        for childnode in node.childNodes:
            self.parse_Node(childnode)
        
    def hdl_featureID(self, node):
        "Handle an identifier tag"
        self.identifier = getXMLText([node])
        
    def hdl_modernLocation(self, node):
        location = getXMLText(node.childNodes)
        self.modernLocation = location
        
    def hdl_rights(self, node):
        self.rights = getXMLText([node])
        
    def hdl_timePeriod(self, node):
        period_name = getXMLText(node.getElementsByTagName('adlgaz:timePeriodName'))
        self.timePeriods.append(period_name)
        
    def hdl_classificationSection(self, node):
        thesaurus =  getXMLText(node.getElementsByTagName('adlgaz:classificationScheme')[0].getElementsByTagName('adlgaz:schemeName'))
        term = getXMLText(node.getElementsByTagName('adlgaz:classificationTerm'))
        self.classifications[thesaurus] = term
        
    def hdl_featureName(self, node):
        self.names.append(Name(self, node))
    
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
            
    
