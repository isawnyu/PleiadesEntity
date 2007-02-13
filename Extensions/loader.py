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

        nids.append(nid)

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

    placeNames = [getattr(names, nid) for nid in nids]
    computedTitle = '/'.join([n.Title() for n in placeNames])
    pid = places.invokeFactory('Place',
                    title=computedTitle,
                    modernLocation=modernLocation,
                    placeType=placeType,
                    creators=creators,
                    contributors=contributors,
                    rights=rights
                    )
    p = getattr(places, pid)
   
    for lid in lids:
        p.addReference(getattr(locations, lid), 'location_location')
    for nid in nids:
        p.addReference(getattr(names, nid), 'name_name')

    return {'place_id': pid, 'location_ids': lids, 'name_ids': nids}

