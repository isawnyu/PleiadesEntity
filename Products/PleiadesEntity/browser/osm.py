from DateTime import DateTime
from lxml import etree
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser import BrowserView
import datetime
import httplib2
import logging


MESSAGE = (
    "Location from OSM created by "
    "Products.PleiadesEntity.browser.osm.OSMLocationFactory"
)

log = logging.getLogger("Pleiades OSM Client")

OSM_API_ENDPOINT = "http://www.openstreetmap.org/api/0.6"
OSM_BROWSE = "http://www.openstreetmap.org/browse"


def read_way_as_linestring(root, way):
    coords = []
    for nd in way.findall('nd'):
        node_id = nd.attrib.get('ref')
        node = root.find("node[@id='%s']" % node_id)
        lon = node.attrib.get("lon")
        lat = node.attrib.get("lat")
        coords.append("[%s,%s]" % (lon, lat))
    return '[' + ','.join(coords) + ']'


class OSMLocationFactory(BrowserView):
    # Makes a location using only an OSM node/way/relation id.
    # Terribly raw at the moment. A mere glance reveals so many places
    # this can fail ungracefully.

    def _fall_back(self, msg):
        # Redirects back to context with a message
        getToolByName(
            self.context, 'plone_utils').addPortalMessage(
                _("Location not created. " + msg.rstrip('.') + "."))
        self.request.response.redirect(self.context.absolute_url())
        return

    def __call__(self):

        try:
            objid = str(int(self.request.get('obj')))
            objtype = str(self.request.get('type'))
        except (TypeError, ValueError) as e:
            self._fall_back(str(e))
            return

        url = "/".join([OSM_API_ENDPOINT, objtype, objid] + (
            [] if objtype == 'node' else ['full']))

        h = httplib2.Http()
        resp, content = h.request(url, "GET")

        if not resp['status'] == "200":
            self._fall_back("OSM API response: " + resp['status'])
            return

        osm = etree.fromstring(content)
        elem = osm.find(objtype)
        assert elem.attrib.get('id') == objid

        version = elem.attrib.get("version")
        changeset = elem.attrib.get("changeset")
        timestamp = elem.attrib.get("timestamp")
        tag_name = getattr(
            elem.find("tag[@k='name']"), "attrib", {}).get("v", None)

        if objtype == "node":
            lon = elem.attrib.get("lon")
            lat = elem.attrib.get("lat")
            geometry = "Point:[%s,%s]" % (lon, lat)
        elif objtype == "way":
            geometry = 'LineString:' + read_way_as_linestring(osm, elem)
        elif objtype == 'relation':
            relation_type = elem.find("tag[@k='type']").attrib.get('v')
            if relation_type != 'multipolygon':
                self._fall_back(
                    "Only relations of type 'multipolygon' can be imported.")
            ways = []
            for member in elem.findall("member[@type='way'"):
                way_id = member.attrib.get('ref')
                way = osm.find("node[@id='%s']" % way_id)
                ways.append(read_way_as_linestring(osm, way))
            geometry = 'MultiLineString:[' + ','.join(ways) + ']'

        ptool = getToolByName(self.context, 'plone_utils')
        repo = getToolByName(self.context, 'portal_repository')
        site = getToolByName(self.context, 'portal_url').getPortalObject()

        title = self.request.get('title') or tag_name or "OSM %s %s" % (
            objtype.capitalize(), objid)
        name = ptool.normalizeString(title)

        try:
            locid = self.context.invokeFactory('Location', name)
            locn = self.context[locid]
            locn.setTitle(title)
            locn.setDescription(u"Location based on OpenStreetMap")
            locn.setGeometry(geometry)
            locn.setInitialProvenance(
                u"OpenStreetMap (%s %s, version %s, "
                u"osm:changeset=%s, %s)" % (
                    objtype.capitalize(), objid,
                    version, changeset, timestamp))
        except Exception as e:
            self._fall_back(str(e))
            return

        try:
            metadataDoc = site['features']['metadata'][
                'generic-osm-accuracy-assessment']
        except KeyError:
            pass
        else:
            locn.addReference(metadataDoc, 'location_accuracy')

        browse_url = "/".join([OSM_BROWSE, objtype, objid])
        citations = [dict(
            identifier=browse_url,
            range="osm:%s=%s" % (objtype, objid),
            type="citesAsDataSource",
        )]

        field = locn.getField('referenceCitations')
        field.resize(len(citations), locn)
        locn.setReferenceCitations(citations)

        now = DateTime(datetime.datetime.now().isoformat())
        locn.setModificationDate(now)
        repo.save(locn, MESSAGE)
        locn.reindexObject()

        self.request.response.redirect("%s/edit" % locn.absolute_url())
