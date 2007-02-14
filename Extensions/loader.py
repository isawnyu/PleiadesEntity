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

BA_MAP_IDS = ['1', '1a'] + [str(n) for n in range(2, 103)]
BA_TABLE_COUNT = 13
BA_ROW_COUNT = 755
BA_ID_MAX = len(BA_MAP_IDS) * BA_TABLE_COUNT * BA_ROW_COUNT

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
            
        type = e.findall("{%s}classificationSection/{%s}classificationTerm" \
                         % (ADLGAZ, ADLGAZ))[0].text
        type = str(type)
        if not transliteration or not type:
            raise EntityLoadError, "Incomplete featureName element"

        id = ptool.normalizeString(transliteration)

        if type not in ['geographic', 'ethnic']:
            raise EntityLoadError, "Invalid name type"
            
        try:
            nid = names.invokeFactory('GeographicName',
                    id=id,
                    title=transliteration.encode('utf-8'),
                    nameAttested=nameAttested.encode('utf-8'),
                    nameLanguage=nameLanguage.encode('utf-8'),
                    creators=creators,
                    contributors=contributors,
                    rights=rights
                    )
            name = getattr(names, nid)
        except:
            nid = names.duplicates.invokeFactory('GeographicName',
                    id=id,
                    title=transliteration.encode('utf-8'),
                    nameAttested=nameAttested.encode('utf-8'),
                    nameLanguage=nameLanguage.encode('utf-8'),
                    creators=creators,
                    contributors=contributors,
                    rights=rights
                    )
            name = getattr(names.duplicates, nid)

        nids.append(nid)
        
        # Time Periods associated with the name
        parse_periods(e, name)
        
        # SecondaryReferences associated with the name
        parse_secondary_references(e, name, ptool)
        
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
        placeType = 'Unknown'

    e = root.findall("{%s}description" % DC)
    if e:
        description = e[0].text.encode('utf-8')
    else:
        description = 'foo'

    # Get the legacy BA identifier
    e = root.findall("{%s}featureID" % ADLGAZ)
    baid = str(e[0].text)
    
    placeNames = [getattr(names, nid) for nid in nids]
    computedTitle = '/'.join([n.Title() for n in placeNames])
    pid = places.invokeFactory('Place',
                    id=baident(baid),
                    title=computedTitle,
                    modernLocation=modernLocation,
                    placeType=placeType,
                    creators=creators,
                    contributors=contributors,
                    rights=rights,
                    description=description
                    )
    p = getattr(places, pid)
   
    for lid in lids:
        p.addReference(getattr(locations, lid), 'location_location')
    for nid in nids:
        p.addReference(getattr(names, nid), 'name_name')
        
    # Secondary references for the place
    parse_secondary_references(root, p, ptool)

    return {'place_id': pid, 'location_ids': lids, 'name_ids': nids}

