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

import logging

import geojson
import simplejson
from shapely.geometry import asShape

from pleiades.capgrids import Grid
from Products.PleiadesEntity.content.interfaces import IPlace
from zgeo.geographer.interfaces import IGeoreferenced, IWriteGeoreferenced
from zope.interface import implements

log = logging.getLogger('PleiadesEntity.geo')


class NotLocatedError(Exception):
    pass


class LocationGeoItem(object):
    implements(IGeoreferenced)

    def __init__(self, context):
        """Expect getGeometry() returns a string like
        'Point:[-105.0, 40.0]'
        """
        self.context = context
        dc_coverage = self.context.getLocation()
        if context.getGeometry():
            t, c = self.context.getGeometry().split(':')
            j = '{"type": "%s", "coordinates": %s}' % (t, c)
            data = simplejson.loads(j)
            self.geo = dict(data)
            g = asShape(data)
            self.geo.update(bbox=g.bounds)
            #self.geo = geojson.loads(
            #            data, object_hook=geojson.GeoJSON.to_instance)
        elif dc_coverage.startswith('http://atlantides.org/capgrids'):
            s = dc_coverage.rstrip('/')
            mapid, gridsquare = s.split('/')[4:6]
            grid = Grid(mapid, gridsquare)
            self.geo = dict(bbox=grid.bounds, relation='relates', type=grid.type, coordinates=grid.coordinates)
        else:
            raise NotLocatedError, "Location cannot be determined"
            
        #try:
        #    _ = self.geo.__geo_interface__
        #except:
        #    raise NotLocatedError, "Location cannot be determined"
            
    @property
    def __geo_interface__(self):
        return self.geo #.__geo_interface__

    @property
    def bounds(self):
        return self.geo['bbox']

    @property
    def type(self):
        return self.geo['type']

    @property
    def coordinates(self):
        return self.geo['coordinates']

    @property
    def crs(self):
        return None


class FeatureGeoItem(object):
    implements(IGeoreferenced)
   
    def __init__(self, context):
        """Initialize adapter."""
        self.context = context
        self._adapter = None
        x = list(self.context.getLocations())
        if len(x) == 0:
            raise ValueError, "Unlocated: could not adapt %s" % str(context)
        else:
            self._adapter = IGeoreferenced(x[0])

    @property
    def type(self):
        return self._adapter.type

    @property
    def coordinates(self):
        return self._adapter.coordinates

    @property
    def crs(self):
        return None

    @property
    def __geo_interface__(self):
        context = self.context
        return dict(
            type='Feature',
            id=context.getId(),
            geometry=self._adapter.__geo_interface__
            )


class PlaceGeoItem(object):
    
    """Python expression of a GeoRSS simple item.
    """
    implements(IGeoreferenced)
   
    def __init__(self, context):
        """Initialize adapter."""
        self.context = context
        self.geo = None
        x = []
        for o in self.context.getLocations():
            try:
                x.append(IGeoreferenced(o))
            except NotLocatedError:
                continue
        if len(x) > 0:
            self.geo = self._geo(x)
        else:
            geo_parts = []
            for ob in self.context.getFeatures():
                try:
                    # rule out reference circles
                    assert self.context not in ob.getParts()
                    geo_parts.append(IGeoreferenced(ob))
                except:
                    pass
            for ob in self.context.getParts():
                try:
                    # rule out reference circles
                    assert self.context not in ob.getParts()
                    geo_parts.append(IGeoreferenced(ob))
                except:
                    pass
            if geo_parts:
                self.geo = self._geo(geo_parts)
        if self.geo is None:
            raise NotLocatedError, "Location cannot be determined"

    def _geo(self, obs):
        # Returns a geometric object or a bounding box for multiple objects
        if len(obs) == 1:
            return obs[0].geo
        else:
            xs = []
            ys = []
            fuzzy = []
            for o in obs:
                if o.__geo_interface__.has_key('relation'):
                    fuzzy.append(o)
                    continue
                try:
                    b = o.bounds #geometry = o.__geo_interface__.get('geometry', o)
                    #b = asShape(geometry).bounds
                except:
                    import pdb; pdb.set_trace()
                    raise
                xs += b[0::2]
                ys += b[1::2]
            for o in fuzzy:
                b = o.bounds
                xs += b[0::2]
                ys += b[1::2]
            try:
                x0, x1, y0, y1 = (min(xs), max(xs), min(ys), max(ys))
            except:
                import pdb; pdb.set_trace()
                raise
            #data = '{"type": "%s", "coordinates": %s}' % (
            #       'Polygon',
            coords = [[[x0, y0], [x0, y1], [x1, y1], [x1, y0], [x0, y0]]] 
            #       )
            return dict(bbox=(x0, y0, x1, y1), relation='relates' * int(bool(fuzzy)) or None, type='Polygon', coordinates=coords) #geojson.loads(data, object_hook=geojson.GeoJSON.to_instance)
    
    @property
    def bounds(self):
        return self.geo['bbox']
    @property
    def type(self):
        return self.geo['type']

    @property
    def coordinates(self):
        return self.geo['coordinates']

    @property
    def crs(self):
        return None

    @property
    def __geo_interface__(self):
        context = self.context
        return dict(
            type='Feature',
            id=context.getId(),
            bbox=self.geo['bbox'],
            geometry=self.geo
            )

def createGeoItem(context):
    """Factory for adapters."""
    if IPlace.providedBy(context):
        return PlaceGeoItem(context)
    else:
        return FeatureGeoItem(context)
