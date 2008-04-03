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

from zope.interface import implements
from zgeo.geographer.interfaces import IGeoreferenced

import logging
log = logging.getLogger('PleiadesEntity.geo')

class PlacefulAssociationGeoItem(object):
    implements(IGeoreferenced)
   
    def __init__(self, context):
        """Initialize adapter."""
        self.context = context

    @property
    def type(self):
        return 'Point'

    @property
    def coordinates(self):
        x = self.context.getRefs('hasLocation')
        if len(x) == 0:
            return ()
        x0 = x[0]
        values = [float(v) for v in \
            x0.getSpatialCoordinates().split()]
        nvalues = len(values)
        # Our Pleiades Locations are 2D
        npoints = nvalues/2
        coords = []
        for i in range(npoints):
            #coords.append(tuple(values[3*i:3*i+3] + [0.0]))
            coords.append((values[3*i+1], values[3*i], 0.0))
        return coords[0]

    @property
    def crs(self):
        return None

    @property
    def __geo_interface__(self):
        context = self.context
        return {
            'type': 'Feature',
            'id': context.getId(),
            'geometry': {'type': self.type, 'coordinates': self.coordinates}
            }


class PlaceGeoItem(object):
    
    """Python expression of a GeoRSS simple item.
    """
    implements(IGeoreferenced)
   
    def __init__(self, context):
        """Initialize adapter."""
        self.context = context
        self._primary_association = None
        for ob in self.context.values():
            try:
                self._primary_association = IGeoreferenced(ob)
            except:
                continue
            break
        if not self._primary_association:
            raise Exception, "Could not adapt %s" % str(context)

    @property
    def type(self):
        return IGeoreferenced(self._primary_association).type

    @property
    def coordinates(self):
        return IGeoreferenced(self._primary_association).coordinates

    @property
    def crs(self):
        return None

    @property
    def __geo_interface__(self):
        return IGeoreferenced(self._primary_association).__geo_interface__

def createGeoItem(context):
    """Factory for adapters."""
    if IPlacefulContainer.providedBy(context):
        return PlaceGeoItem(context)
    else:
        return PlacefulAssociationGeoItem(context)



