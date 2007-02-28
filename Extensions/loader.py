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

import lxml.etree as etree

from Products.CMFCore.utils import getToolByName

from Products.PleiadesEntity.Extensions.xmlutil import *
from Products.PleiadesEntity.Extensions.cooking import *

from Products.PleiadesEntity.config import *

batlas_pattern = re.compile(r'batlas-(\w+)-(\w+)-(\w+)')

def baident(identifier):
    """Map old identifiers of the form batlas-MM-TT-RR to unique integers."""
    m = batlas_pattern.search(identifier)
    g = m.groups()
    mm = BA_MAP_IDS.index(g[0])
    tt = int(g[1]) - 1
    rr = int(g[2]) - 1
    return (BA_ROW_COUNT * BA_TABLE_COUNT) * mm + BA_ROW_COUNT * tt + rr
    
class EntityLoadError(Exception):
    pass


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
   
def initialize(self):
    """Setup the places, names, and locations containers."""
    lpf = self.portal_types['Large Plone Folder']
    lpf_allow = lpf.global_allow
    lpf.global_allow = True

    n = self.portal_types['GeographicName']
    n_allow = n.global_allow
    n.global_allow = True

    n = self.portal_types['EthnicName']
    n_allow = n.global_allow
    n.global_allow = True

    try:
        self.invokeFactory('Large Plone Folder',
            id='names', title='Ancient Names')
        self.names.invokeFactory('Large Plone Folder',
            id='duplicates', title='Duplicate Names')
    except:
        pass
    try:
        self.invokeFactory('LocationContainer',
            id='locations', title='Ancient Locations')
    except:
        pass
    try:
        self.invokeFactory('PlaceContainer',
            id='places', title='Ancient Places')
        getattr(self, 'places')._v_nextid = BA_ID_MAX
    except:
        pass

def loaden(self, sourcedir):
    """Attempt to load all XML files in the specified source directory.
    Files which can not be loaded are reported."""
    failures = []
    count = 0
    for xml in glob.glob("%s/*.xml" % sourcedir):
        try:
            load_place(self, xml)
            count += 1
        except Exception, e:
            failures.append([basename(xml), str(e)])
    
    if len(failures) == 0:
        return "Loaded %d of %d files." % (count, count)
    else:
        msg = "Loaded %d of %d files. Failures:\n" % (count, count + len(failures))
        for f in failures:
            msg += "%s\n" % str(f)
        return msg
    
AWMC = "http://www.unc.edu/awmc/gazetteer/schemata/ns/0.3"
ADLGAZ = "http://www.alexandria.ucsb.edu/gazetteer/ContentStandard/version3.2/"
GEORSS = "http://www.georss.org/georss"
DC = "http://purl.org/dc/elements/1.1/"
XML = "http://www.w3.org/XML/1998/namespace"
TEI = "http://www.tei-c.org/ns/1.0"

periods = {"Archaic":"Archaic (pre-550 BC)", 
    "Classical":"Classical (550 - 330 BC)",
    "Hellenistic (Roman Republic)":"Hellenistic/Republican (330 - 30 BC)",
    "Roman":"Roman (30 BC - AD 300)",
    "Late Antique":"Late Antique (AD 300 - 625)"}
period_ids = {"Archaic":"archaic", 
    "Classical":"classical",
    "Hellenistic (Roman Republic)":"hellenistic-republican",
    "Roman":"roman",
    "Late Antique":"late-antique"}

def parse_periods(xmlcontext, portalcontext):
    """Find timePeriod children of the node at xmlcontext and create
    appropriate temporalAttestation children of the object at 
    portalcontext."""
    
    for tp in  xmlcontext.findall("{%s}timePeriod" % ADLGAZ):
        tpn = tp.xpath("*[local-name()='timePeriodName']")
        if not tpn:
            raise EntityLoadError, "Incomplete timePeriod element for timePeriod node %s" % xmlcontext.findall("{%s}timePeriod" % ADLGAZ).index(tp)
        cert = 'certain'
        tpnstr = tpn[0].text
        if tpnstr.endswith('?'):
            cert = 'less certain'
            tpnstr = tpnstr.replace('?', '')
        if tp.xpath("ancestor::*[local-name()='featureName']"):
            # this is a period for a name
            inferred = tp.xpath("../descendant::*[@ref='na-inferred']")
        else:
            # location date inference was not noted in BAtlas
            inferred = tp.xpath("bogus")
        if inferred and cert=='less certain':
            certainty = cert + ' and there is no contemporary evidence'
        elif inferred and cert=='certain':
            certainty = cert + ', but there is no contemporary evidence'
        else:
            certainty = cert
        period=periods[tpnstr]
        id=period_ids[tpnstr]
        try:
            portalcontext.invokeFactory('TemporalAttestation',
                title=period,
                id=id,
                certainty=certainty
                )
        except:
            raise EntityLoadError, "There is already a TemporalAttestation with id=%s in portal context" % id

def parse_secondary_references(xmlcontext, portalcontext, ptool):
    srs =  xmlcontext.find("{%s}secondaryReferences" % AWMC)
    if srs:
        bibls = srs.findall("{%s}bibl" % TEI)
        if not bibls:
            raise EntityLoadError, "Encountered an empty secondaryReferences" 
        else:
            for bibl in bibls:
                biblstr = bibl.text
                id = ptool.normalizeString(biblstr)
                try:
                    portalcontext.invokeFactory('SecondaryReference',
                        title=biblstr,
                        id=id
                    )
                except:
                    raise EntityLoadError, "There is already a SecondaryReference with id=%s in portal context" % id
            
import sys

def load_place(site, file):
    """Create a new Place in plonefolder and populate it with
    the data found in the xml file at sourcepath."""

    root = etree.parse(file).getroot()
    ptool = getToolByName(site, 'plone_utils')

    places = site.places
    names = site.names
    locations = site.locations

    # Authorship
    creators = [e.text for e in root.findall("{%s}creator" % DC)]
    contributors = [e.text for e in root.findall("{%s}contributor" % DC)]
    
    # Rights
    e = root.findall("{%s}rights" % DC)
    if e:
        rights = e[0].text
    else:
        rights = None
        
    # lists of location and name ids
    lids = []
    nids = []
    association_certainties = []

    # Names
    for e in root.findall("{%s}featureName" % ADLGAZ):
        transliteration = e.findall("{%s}transliteration" % AWMC)[0].text
        na = e.findall("{%s}name" % ADLGAZ)
        if na:
            nameAttested = na[0].text
            nalang = na[0].get("{%s}lang" % XML)
            if nalang:
                nameLanguage = nalang
            else:
                nameLanguage = ''
        else:
            nameAttested = ''
            nameLanguage = ''
        
        d = e.findall("{%s}description" % DC)
        if d:
            description = d[0].text.encode('utf-8')
        else:
            description = ''

        type = e.findall("{%s}classificationSection/{%s}classificationTerm" \
                         % (ADLGAZ, ADLGAZ))[0].text
        type = str(type)
        if not transliteration or not type:
            raise EntityLoadError, "Incomplete featureName element"
            
        # accuracy = ('accurate' | 'inaccurate' | 'false')
        accuracy = 'accurate'
        if type == 'false':
            accuracy = 'false'
        else:
            a = e.xpath("descendant::*[@ref='na-inaccurate']")
            if a:
                accuracy = 'inaccurate'
        
        # completeness = ('complete' | 'reconstructable' | 'non-reconstructable')
        completeness = 'complete'
        a = e.xpath("descendant::*[@ref='na-reconstructed']")
        if a:
            completeness = 'reconstructable'
        else:
            a = e.xpath("descendant::*[@ref='na-fragmentary']")
            if a:
                completeness = 'non-reconstructable'

        id = ptool.normalizeString(transliteration)

        if type not in ['geographic', 'ethnic', 'false']:
            raise EntityLoadError, "Invalid name type"
        # false -> geographic
        if type == 'false': type = 'geographic'
        typename = "%sName" % type.capitalize()

        certainty = 'certain'
        try:
            certainty = e.findall("{%s}classificationSection/{%s}nameAssociation" % (ADLGAZ, AWMC))[0].get('ref', 'certain')
        except:
            pass

        try:
            nid = names.invokeFactory(typename,
                    id=id,
                    title=transliteration.encode('utf-8'),
                    nameAttested=nameAttested.encode('utf-8'),
                    nameLanguage=nameLanguage.encode('utf-8'),
                    accuracy=accuracy,
                    completeness=completeness,
                    creators=creators,
                    contributors=contributors,
                    rights=rights,
                    description=description
                    )
            name = getattr(names, nid)
        except:
            nid = names.duplicates.invokeFactory(typename,
                    id=id,
                    title=transliteration.encode('utf-8'),
                    nameAttested=nameAttested.encode('utf-8'),
                    nameLanguage=nameLanguage.encode('utf-8'),
                    accuracy=accuracy,
                    completeness=completeness,
                    creators=creators,
                    contributors=contributors,
                    rights=rights,
                    description=description
                    )
            name = getattr(names.duplicates, nid)

        nids.append(nid)
        association_certainties.append(certainty)

        # Time Periods associated with the name
        parse_periods(e, name)
        
        # SecondaryReferences associated with the name
        parse_secondary_references(e, name, ptool)
        name.reindexObject()
        
    # Locations
    for e in root.findall("{%s}spatialLocation" % ADLGAZ):
        coords = e.findall("{%s}point" % GEORSS)[0].text

        lid = locations.invokeFactory('Location',
                    geometryType='Point',
                    spatialCoordinates=str(coords),
                    creators=creators,
                    contributors=contributors,
                    rights=rights
                    )
        
        lids.append(lid)
        
        # Time Periods associated with the location
        parse_periods(root, getattr(locations, lid))
        
        getattr(locations, lid).reindexObject()

    # Place
    e = root.findall("{%s}modernLocation" % AWMC)
    if e:
        modernLocation = str(e[0].text.encode('utf-8'))
    else:
        modernLocation = 'None'

    e = root.findall("{%s}classificationSection/{%s}classificationTerm" \
                     % (ADLGAZ, ADLGAZ))
    if e:
        placeType = str(e[0].text)
    else:
        placeType = 'unknown'
    legaltypes = ['aqueduct', 'bath', 'bay', 'bridge', 'canal', 'cape', 'cave', 'cemetery', 'centuriation', 'church', 'coast', 'dam', 'estate', 'estuary', 'false', 'findspot', 'forest', 'fort', 'hill', 'island', 'lighthouse', 'mine', 'mountain', 'oasis', 'pass', 'people', 'plain', 'port', 'production', 'region', 'reservoir', 'ridge', 'river', 'road', 'salt-marsh', 'settlement', 'settlement-modern', 'spring', 'station', 'temple', 'tumulus', 'undefined', 'unknown', 'unlocated', 'valley', 'wall', 'water-inland', 'water-open', 'well', 'wheel', 'whirlpool']
    try:
        ptidx = legaltypes.index(placeType)
    except:
        raise EntityLoadError, "Invalid placeType  = %s" % placeType
            
    e = root.findall("{%s}description" % DC)
    if e:
        description = e[0].text.encode('utf-8')
    else:
        description = ''

    # Get the legacy BA identifier
    e = root.findall("{%s}featureID" % ADLGAZ)
    fid = str(e[0].text)
    if fid.startswith('batlas'):
        id = baident(fid)
    else:
        id = None

    placeNames = [getattr(names, nid) for nid in nids]
    computedTitle = '/'.join([n.Title() for n in placeNames])
    pid = places.invokeFactory('Place',
                    id=id,
                    title=computedTitle,
                    modernLocation=modernLocation,
                    creators=creators,
                    contributors=contributors,
                    rights=rights,
                    description=description
                    )
    p = getattr(places, pid)
    p.reindexObject()
   
    for lid in lids:
        # Handle the unnamed case
        if len(nids) == 0:
            aid = p.invokeFactory('PlacefulAssociation',
                id="unnamed-%s" % lid,
                placeType=placeType,
                certainty='certain',
                )
            a = getattr(p, aid)
            a.addReference(getattr(locations, lid), 'hasLocation')
        
            # Secondary references for the place
            parse_secondary_references(root, a, ptool)
            a.reindexObject()
        
        else:
            for i, nid in enumerate(nids):
                # Get association certainty from XML
                certainty = association_certainties[i]
            
                aid = p.invokeFactory('PlacefulAssociation',
                    id="%s-%s" % (nid,lid),
                    placeType=placeType,
                    certainty=certainty,
                    )
                a = getattr(p, aid)
                a.addReference(getattr(locations, lid), 'hasLocation')
                a.addReference(getattr(names, nid), 'hasName')
        
                # Secondary references for the place
                parse_secondary_references(root, a, ptool)
                a.reindexObject()

    return {'place_id': pid, 'location_ids': lids, 'name_ids': nids}

