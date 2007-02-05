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
        
def load_place(container, file):
    """Create a new Place in plonefolder and populate it with
    the data found in the xml file at sourcepath."""

    tree = etree.parse(file)
    return '0'

