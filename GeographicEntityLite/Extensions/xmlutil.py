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

import re
from xml.dom.minidom import parse

language_vocab = {'grc':'Ancient Greek', 'la':'Latin', 'grc-Latn':'Ancient Greek in Latin characters', 'la-Grek':'Latin in Ancient Greek characters'}

def getXMLDOM(file_path):
    """
    Opens and reads the indicated file, parsing the contents into a minidom, which is returned to the
    calling function.
    """
    xmlfile = open(file_path, 'r')
    xmldom = parse(xmlfile)
    xmlfile.close()
    return xmldom
    
def getXMLText(nodelist):
    """
    Provides a concatenated string version of the content of all subordinate text nodes in the passed
    node list.
    """
    
    alltext = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            alltext += node.data
        else:
            alltext += getXMLText(node.childNodes)
            
    
    return purifyText(alltext)
    
def getXMLValue(node):
    """
    Returns the concatenated string version of any text node children of the current node.
    """
    alltext = ""
    for childnode in node.childNodes:
        if childnode.nodeType == childnode.TEXT_NODE:
            alltext += childnode.data
    return alltext
   
def purifyText(text):
    penances = [(u'\U000000A0', u' ', 'No-Break Space')]
    for penance in penances:
        p = re.compile(penance[0])
        text = p.sub(penance[1], text)
    return text
