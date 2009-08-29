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
from zgeo.geographer.interfaces import IGeoreferenced, IWriteGeoreferenced
import geojson
from Products.PleiadesEntity.content.interfaces import IPlace
import logging
log = logging.getLogger('PleiadesEntity.geo')


class LocationGeoItem(object):
    implements(IGeoreferenced)

    def __init__(self, context):
        self.context = context

    @property
    def __geo_interface__(self):
        """Expect getGeometry() returns a string like
        'Point:[-105.0, 40.0]'
        """
        d = self.context.getGeometry().split(':')
        data = '{"type": "%s", "coordinates": %s}' % tuple(d)
        x = geojson.loads(data, object_hook=geojson.GeoJSON.to_instance)
        return x.__geo_interface__

    @property
    def type(self):
        return self.__geo_interface__['type']

    @property
    def coordinates(self):
        return self.__geo_interface__['coordinates']

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
        self._adapter = None
        x = list(self.context.getLocations())
        if len(x) > 0:
            self._adapter = IGeoreferenced(x[0])
        else:
            for ob in self.context.getFeatures():
                try:
                    self._adapter = IGeoreferenced(ob)
                except:
                    continue
                    break
        if not self._adapter:
            raise ValueError, "Could not adapt %s" % str(context)

    @property
    def type(self):
        return IGeoreferenced(self._adapter).type

    @property
    def coordinates(self):
        return IGeoreferenced(self._adapter).coordinates

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

def createGeoItem(context):
    """Factory for adapters."""
    if IPlace.providedBy(context):
        return PlaceGeoItem(context)
    else:
        return FeatureGeoItem(context)
