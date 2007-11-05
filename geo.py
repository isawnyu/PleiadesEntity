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

from Products.PleiadesGeocoder.interfaces import IGeoItemSimple \
    , IGeoCollectionSimple
from Products.PleiadesEntity.interfaces import IPlaceContainer \
    , IPlacefulContainer


class PlacefulAssociationGeoItem(object):
    
    """Python expression of a GeoRSS simple item.
    """
    implements(IGeoItemSimple)
   
    def __init__(self, context):
        """Initialize adapter."""
        self.context = context

    @property
    def geom_type(self):
        return 'Point'

    def getSpatialCoordinates(self):
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
            coords.append(tuple(values[3*i:3*i+3] + [0.0]))
        return tuple(coords)

    @property
    def spatialCoordinates(self):
        """GeoRSS Simple coordinate string (2D)."""
        x = self.context.getRefs('hasLocation')
        if len(x) == 0:
            return ''
        return x[0].getSpatialCoordinates()
        
    @property
    def coords(self):
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

    def isGeoreferenced(self):
        """Return True if the object is "on the map"."""
        return bool(len(self.context.getRefs('hasLocation')))

    @property
    def __geo_interface__(self):
        context = self.context
        return {
            'type': 'Feature',
            'id': context.getId(),
            'properties': {
                'title': context.title_or_id(),
                'description': context.Description(),
                'link': context.absolute_url(),
                },
            'geometry': {'type': self.geom_type, 'coordinates': self.coords}
            }


class PlaceGeoItem(object):
    
    """Python expression of a GeoRSS simple item.
    """
    implements(IGeoItemSimple)
   
    def __init__(self, context):
        """Initialize adapter."""
        self.context = context
        self._primary_association = None
        for ob in context.listFolderContents():
            try:
                self._primary_association = IGeoItemSimple(ob)
            except:
                continue
            break
        if not self._primary_association:
            raise Exception, "Could not adapt %s" % str(context)

    def isGeoreferenced(self):
        """Return True if the object is "on the map"."""
        return self._primary_association.isGeoreferenced()

    @property
    def geom_type(self):
        return self._primary_association.geom_type

    @property
    def coords(self):
        return self._primary_association.coords

    @property
    def __geo_interface__(self):
        context = self.context
        return {
            'type': 'Feature',
            'id': context.getId(),
            'properties': {
                'title': context.title_or_id(),
                'description': context.Description(),
                'link': context.absolute_url(),
                },
            'geometry': {
                'type': self._primary_association.geom_type, 
                'coordinates': self._primary_association.coords
                }
            }


def createGeoItem(context):
    """Factory for adapters."""
    if IPlacefulContainer.providedBy(context):
        return PlaceGeoItem(context)
    else:
        return PlacefulAssociationGeoItem(context)


class GeoCollectionSimple(object):
    
    """Adapter for Folderish collections of GeoItemSimple.
    """
    implements(IGeoCollectionSimple)
    
    def __init__(self, context):
        """Initialize."""
        self.context = context
        
    def geoItems(self):
        if IPlaceContainer.providedBy(self.context):
        #hasattr(self.context, 'listFolderContents'):
            for ob in self.context.listFolderContents():
                try:
                    item = IGeoItemSimple(ob)
                    assert(item.isGeoreferenced())
                except:
                    continue
                yield item
        else:
            try:
                item = IGeoItemSimple(self.context)
                assert(item.isGeoreferenced())
                yield item
            except:
                pass

