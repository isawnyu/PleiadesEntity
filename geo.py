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

    def getSRS(self):
        return 'EPSG:4326'

    def setSRS(self, srs):
        pass
        
    def getGeometryType(self):
        return 'point'

    def setGeometryType(self, geomtype):
        pass

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

    def setGeometry(self, geomtype, coords):
        value = ''
        for point in coords:
            if len(point) == 3:
                value = ' '.join([value, "%f %f %f" % point])
            elif len(point) == 2:
                value = ' '.join([value, "%f %f 0.0" % point])
            else:
                raise ValueError, \
                "Insufficient number of ordinates: %s" % str(point)
        x0 = self.context.getRefs('hasLocation')[0]
        x0.setSpatialCoordinates(value.lstrip())
        
    def isGeoreferenced(self):
        """Return True if the object is "on the map"."""
        return bool(len(self.context.getRefs('hasLocation')))
        
    def getInfo(self, dims=3):
        """Return an informative dict."""
        context = self.context
        info = {'srs':                  self.getSRS(),
                'geometryType':         self.getGeometryType(),
               }
        points = self.getSpatialCoordinates()
        coords = []
        for i in range(len(points)):
            coords.extend([str(v) for v in points[i][0:dims]])
        info['spatialCoordinates'] = ' '.join(coords)

        # Content objects
        info.update(
               {'id':           context.getId(),
                'title':        context.title_or_id(),
                'description':  context.Description(),
                'url':          context.absolute_url(),}
            )
        return info

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

    def getSRS(self):
        return 'EPSG:4326'

    def setSRS(self, srs):
        pass
        
    def getGeometryType(self):
        return 'point'

    def setGeometryType(self, geomtype):
        pass

    def getSpatialCoordinates(self):
        return self._primary_association.getSpatialCoordinates()

    def setGeometry(self, geomtype, coords):
        raise NotImplementedError
        
    def isGeoreferenced(self):
        """Return True if the object is "on the map"."""
        return self._primary_association.isGeoreferenced()
        
    def getInfo(self, dims=3):
        """Return an informative dict."""
        context = self.context
        info = self._primary_association.getInfo()
        info.update(
               {'id':           context.getId(),
                'title':        context.title_or_id(),
                'description':  context.Description(),
                'url':          context.absolute_url(),}
            )
        return info


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
            except:
                pass
            yield item

    def getItemsInfo(self):
        infos = []
        for item in self.geoItems():
            infos.append(item.getInfo())
        return infos

    def getBoundingBox(self):
        raise NotImplementedError
        
