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
import logging

import lxml.etree as etree

import transaction

from Products.CMFCore.utils import getToolByName

from Products.PleiadesEntity.Extensions.xmlutil import *
from Products.PleiadesEntity.Extensions.ws_validation import validate_name
from Products.PleiadesEntity.AppConfig import *
from Products.PleiadesEntity.config import *

batlas_pattern = re.compile(r'batlas-(\w+)-(\w+)-(\w+)')
batlas_anon_pattern = re.compile(r'batlas-(\w+)-anon-(\w+)')


def baident(identifier):
    """Map old identifiers of the form batlas-MM-TT-RR to unique integers."""
    m = batlas_pattern.search(identifier)
    g = m.groups()
    mm = BA_MAP_IDS.index(g[0])
    tt = int(g[1]) - 1
    rr = int(g[2]) - 1
    return (BA_ROW_COUNT * BA_TABLE_COUNT) * mm + BA_ROW_COUNT * tt + rr

def baident_anon(xmlcontext):
    """Map old identifiers of the form batlas-MM-TT-RR to unique integers."""
    e = xmlcontext.findall("{%s}featureID" % ADLGAZ)
    identifier = str(e[0].text)
    m = batlas_anon_pattern.search(identifier)
    g = m.groups()
    m = g[0]

    coords = xmlcontext.xpath(
        "adlgaz:spatialLocation/georss:point",
        namespaces={'adlgaz': ADLGAZ, 'georss': GEORSS}
        )[0].text.split()

    p = "%.4f%.4f" % (float(coords[0]) + 180.0, float(coords[1]) + 90.0)
    return "%s%s" % (m, p.replace('.', '')) 

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
    
    n = self.portal_types['Name']
    n_allow = n.global_allow
    n.global_allow = True


def loaden(site, sourcedir):
    """Attempt to load all XML files in the specified source directory.
    Files which can not be loaded are reported."""
    failures = []
    count = 0
    log = logging.getLogger("pleiades.entity")
    for xml in glob.glob("%s/*.xml" % sourcedir):
        try:
            load_place(site, xml)
            count += 1
        except Exception, e:
            log.error("Failed to load %s", xml, exc_info=1)
    
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

NAMESPACES = {
    'awmc': AWMC,
    'adlgaz': ADLGAZ,
    'georss': GEORSS,
    'dc': DC,
    'xml': XML,
    'tei': TEI
    }

periods = {
    "Archaic": "Archaic (pre-550 BC)", 
    "Classical": "Classical (550 - 330 BC)",
    "Hellenistic (Roman Republic)": "Hellenistic (Roman Republic; 330 - 30 BC)",
    "Roman": "Roman (Early Empire; 30 BC - AD 300)",
    "Late Antique": "Late Antique (AD 300 - 640)"
    }
period_ids = {
    "Archaic": "archaic", 
    "Classical": "classical",
    "Hellenistic (Roman Republic)": "hellenistic-republican",
    "Roman": "roman",
    "Late Antique": "late-antique"
    }

def parse_periods(xmlcontext, portalcontext, **kw):
    """Find timePeriod children of the node at xmlcontext and create
    appropriate temporalAttestation children of the object at 
    portalcontext."""

    for tp in  xmlcontext.findall("{%s}timePeriod" % ADLGAZ):
        tpn = tp.xpath("*[local-name()='timePeriodName']")
        if not tpn:
            raise EntityLoadError, "Incomplete timePeriod element for timePeriod node %s" % xmlcontext.findall("{%s}timePeriod" % ADLGAZ).index(tp)
        conf = 'confident'
        tpnstr = tpn[0].text
        if tpnstr.endswith('?'):
            conf = 'less-confident'
            tpnstr = tpnstr.replace('?', '')
        if tp.xpath("ancestor::*[local-name()='featureName']"):
            # this is a period for a name
            inferred = tp.xpath("../descendant::*[@ref='na-inferred']")
        else:
            # location date inference was not noted in BAtlas
            inferred = tp.xpath("bogus")
        if inferred:
            confidence = conf + '-inferred'
        else:
            confidence = conf
        period=periods[tpnstr]
        id=period_ids[tpnstr]
        
        try:
            portalcontext.invokeFactory('TemporalAttestation',
                id=id,
                timePeriod=id,
                attestationConfidence=confidence,
                **kw
                )
        except:
            raise
            #raise EntityLoadError, "There is already a TemporalAttestation with id=%s in portal context = %s" % (id, portalcontext.Title())

def getalltext(elem):
    text = elem.text or ""
    for e in elem:
        text = text + " " + getalltext(e)
    return text.strip()

def parse_secondary_references(xmlcontext, portalcontext, ptool, **kw):
    srs =  xmlcontext.find("{%s}secondaryReferences" % AWMC)
    if srs is not None:
        bibls = srs.xpath('tei:bibl', namespaces={'tei': TEI})
        #if not bibls:
        #    return
        #    #raise EntityLoadError, "Encountered an empty secondaryReferences"
        if bibls is not None:
            for bibl in bibls:
                title_elem = bibl.xpath('tei:title', namespaces={'tei': TEI})
                if not title_elem:
                    continue
                url = title_elem[0].attrib.get('{http://www.w3.org/1999/xlink}href', '')
                bibstr = getalltext(bibl)
                id = ptool.normalizeString(bibstr)
                try:
                    portalcontext.invokeFactory('SecondaryReference',
                        title=bibstr,
                        id=id,
                        item=url,
                        range=bibstr,
                        **kw
                    )
                except:
                    raise

def parse_attrib_rights(xmlcontext):
    root = xmlcontext
    creators = [e.text for e in root.findall("{%s}creator" % DC)]
    contributors = [e.text for e in root.findall("{%s}contributor" % DC)]
    e = root.findall("{%s}rights" % DC)
    if e:
        rights = e[0].text
    else:
        rights = None
    return (creators, contributors, rights)

def find_next_valid_name_id(context, initial):
    if not hasattr(context, initial):
        return initial
    else:
        for i in range(1, 43):
            candidate = "%s-%d" % (initial, i)
            if not hasattr(context, candidate):
                return candidate
        # Shouldn't get here
        raise Exception, "Number of allowable name duplicates exceeded"

def parse_names(xmlcontext, portalcontext, ptool, **kw):
    root = xmlcontext
    names = portalcontext
    nids = []
    association_certainties = []
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
            
        if nameAttested and nameLanguage:
            invalid = validate_name(nameLanguage, nameAttested.encode('utf-8'))
            if invalid:
                raise EntityLoadError, invalid.decode('utf-8').encode('ascii', 'backslashreplace')
        
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

        if type not in ['geographic', 'ethnic', 'false', 'undefined']:
            raise EntityLoadError, "Invalid name type = %s" % type
        # false -> geographic
        if type == 'false': type = 'geographic'
        
        certainty = 'certain'
        try:
            certainty = e.findall("{%s}classificationSection/{%s}nameAssociation" % (ADLGAZ, AWMC))[0].get('ref', 'certain')
        except:
            pass

        #vid = find_next_valid_name_id(names, id)
        nid = names.invokeFactory("Name",
                #id=vid,
                title = transliteration.encode('utf-8'),
                nameTransliterated=transliteration.encode('utf-8'),
                nameAttested=nameAttested.encode('utf-8'),
                nameLanguage=nameLanguage.encode('utf-8'),
                nameType=type,
                accuracy=accuracy,
                completeness=completeness,
                description=description,
                **kw
                )
        name = names[nid]

        nids.append(nid)
        association_certainties.append(certainty)

        # Time Periods associated with the name
        parse_periods(e, name, **kw)
        # SecondaryReferences associated with the name
        parse_secondary_references(e, name, ptool, **kw)
        
    return (nids, association_certainties)

def parse_locations(xmlcontext, portalcontext, ptool, **kw):
    root = xmlcontext
    lids = []
    for e in root.findall("{%s}spatialLocation" % ADLGAZ):
        coords = e.findall("{%s}point" % GEORSS)[0].text.split()
        lid = portalcontext.invokeFactory('Location',
                    geometry='Point:[%s,%s]' % (coords[1], coords[0]),
                    **kw
                    )
        lids.append(lid)
        # Time Periods associated with the location
        parse_periods(root, portalcontext[lid], **kw)
        # SecondaryReferences associated with the name
        parse_secondary_references(e, portalcontext[lid], ptool, **kw)

    return lids

def load_place(site, file):
    """Create a new Place in plonefolder and populate it with
    the data found in the xml file at sourcepath."""

    ptool = getToolByName(site, 'plone_utils')

    places = site['places']
    features = site['features']
    names = site['names']
    locations = site['locations']
    fids = []

    savepoint = transaction.savepoint()
    try:
        root = etree.parse(file).getroot()
        creators, contributors, rights = parse_attrib_rights(root)
        # Names
        nids, association_certainties = parse_names(root, names, ptool, creators=creators, contributors=contributors, rights=rights)
        # Locations
        lids = parse_locations(root, locations, ptool, creators=creators, contributors=contributors, rights=rights)
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
        legaltypes = ['aqueduct', 'bath', 'bay', 'bridge', 'canal', 'cape', 'cave', 'cemetery', 'centuriation', 'church', 'coast', 'dam', 'estate', 'estuary', 'false', 'findspot', 'forest', 'fort', 'hill', 'island', 'lighthouse', 'mine', 'mountain', 'oasis', 'pass', 'people', 'plain', 'port', 'production', 'region', 'reservoir', 'ridge', 'river', 'road', 'salt-marsh', 'settlement', 'settlement-modern', 'spring', 'station', 'temple', 'tumulus', 'undefined', 'unknown', 'unlocated', 'valley', 'villa', 'wall', 'water-inland', 'water-open', 'well', 'wheel', 'whirlpool']
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
            if fid.find('anon') >= 0:
                id = baident_anon(root)
            else:
                id = baident(fid)
        else:
            id = None
    
        placeNames = [names[nid] for nid in nids]
        computedTitle = '/'.join([n.Title() for n in placeNames])
        
        pid = places.invokeFactory('Place',
                    id=id,
                    title=computedTitle,
                    modernLocation=modernLocation,
                    description=description,
                    creators=creators,
                    contributors=contributors,
                    rights=rights,
                    )
        p = places[pid]

        # Iterate over locations
        for lid in lids:
            # Handle the unnamed case
            if len(nids) == 0:
                fid = features.invokeFactory('Feature',
                    featureType=placeType,
                    associationCertainty='certain',
                    description=description,
                    creators=creators,
                    contributors=contributors,
                    rights=rights,
                    )
                f = features[fid]
                f.addReference(locations[lid], 'hasLocation')
                # Secondary references for the place
                parse_secondary_references(root, f, ptool,
                    creators=creators,
                    contributors=contributors,
                    rights=rights
                    )
                p.addReference(f, 'hasFeature')
                fids.append(fid)
            else:
                for i, nid in enumerate(nids):
                    # Get association certainty from XML
                    certainty = association_certainties[i]
                    fid = features.invokeFactory('Feature',
                        featureType=placeType,
                        associationCertainty=certainty,
                        description=description,
                        creators=creators,
                        contributors=contributors,
                        rights=rights,
                        )
                    f = features[fid]
                    f.addReference(locations[lid], 'hasLocation')
                    f.addReference(names[nid], 'hasName')
                    # Secondary references for the place
                    parse_secondary_references(root, f, ptool,
                        creators=creators,
                        contributors=contributors,
                        rights=rights
                        )
                    p.addReference(f, 'hasFeature')
                    fids.append(fid)
        # If there are no locations, iterate over the names
        if len(lids) == 0:
            for nid in nids:
                fid = features.invokeFactory('Feature',
                        featureType=placeType,
                        associationCertainty='certain',
                        description=description,
                        creators=creators,
                        contributors=contributors,
                        rights=rights,
                        )
                f = features[fid]
                f.addReference(names[nid], 'hasName')
                # Secondary references for the place
                parse_secondary_references(root, f, ptool,
                    creators=creators,
                    contributors=contributors,
                    rights=rights
                    )
                p.addReference(f, 'hasFeature')
                fids.append(fid)
    except:
        savepoint.rollback()
        raise

    transaction.commit()
    return dict(place_id=pid, feature_ids=fids, location_ids=lids, name_ids=nids)
