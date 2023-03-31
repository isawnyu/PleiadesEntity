# -*- coding: utf-8 -*-
import datetime
import logging
import pkg_resources
import requests
from DateTime import DateTime
from lxml import etree
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import BadRequest


MESSAGE = (
    "Location from OSM created by "
    "Products.PleiadesEntity.browser.osm.OSMLocationFactory"
)

log = logging.getLogger("Pleiades OSM Client")

user_agent = (
    'PleiadesEntityBot/{} (+https://pleiades.stoa.org/help/bots)'
    ''.format(pkg_resources.get_distribution('Products.PleiadesEntity').version))
HEADERS = {
    'from': 'pleiades.admin@nyu.edu',
    'user-agent': user_agent
}
TIMEOUT = 3.0
LOCATION_ERROR = "OSM import failed because of an error in parsing coordinate geometry: "
OSM_API_ENDPOINT = "https://www.openstreetmap.org/api/0.6"
OSM_BROWSE = "https://www.openstreetmap.org/browse"
SUPPORTED_RELATION_TYPES = {
    "boundary",
    "multipolygon",
    "site",
    "watershed",
    "waterway",
}
VALID_WATERWAYS = [
    'river',
    'stream',
    'tidal_channel',
    'canal',
    'waterfall',
    'rapids',
]


def read_way_as_linestring(root, way):
    coords = []
    for nd in way.findall('nd'):
        node_id = nd.attrib.get('ref')
        node = root.find("node[@id='%s']" % node_id)
        lon = node.attrib.get("lon")
        lat = node.attrib.get("lat")
        coords.append("[%s,%s]" % (lon, lat))
    return '[' + ','.join(coords) + ']'


def show_osm_error(context, request, msg):
    """Display a status message error and redirect to
    the view of the context.
    """
    IStatusMessage(request).addStatusMessage(
        _(LOCATION_ERROR + msg.rstrip('.') + "."),
        type="error"
    )
    request.response.redirect(context.absolute_url())

class OSMRetrievalError(Exception):
    """OSM data could not be retrieved or was invalid."""
    pass


def fetch_osm_by_type_and_id(objtype, objid):
    """Fetch data from OSM API for a type + ID combintation.

    @return dict  OSM data:
    {
        "changeset": "128834901",
        "geometry": "Point:[103.8669282,13.4114999]",
        "tag_name": u"ច្រកទ្វារខាងត្បូង",
        "timestamp": "2022-11-13T07:03:06Z",
        "version": "22"
    }
    """
    result = {}
    objtype = objtype.lower()
    url = "/".join(
        [OSM_API_ENDPOINT, objtype, objid] +
        ([] if objtype == "node" else ["full"])
    )
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    if not resp.status_code == 200:
        raise OSMRetrievalError(
            'Error retrieving "{type}" resource with ID {id} (URL: {url}). '
            'Is "{type}" the correct type? (OSM API response: {status})'.format(
                type=objtype, id=objid, url=url, status=resp.status_code
            )
        )

    osm = etree.fromstring(resp.content)
    elem = osm.find('{}[@id="{}"]'.format(objtype, objid))
    if elem is None:
        raise OSMRetrievalError('{} {} not found'.format(objtype, objid))

    result["version"] = elem.attrib.get("version")
    result["changeset"] = elem.attrib.get("changeset")
    result["timestamp"] = elem.attrib.get("timestamp")
    result["tag_name"] = getattr(
        elem.find("tag[@k='name']"), "attrib", {}).get("v", None)

    if objtype == "node":
        lon = elem.attrib.get("lon")
        lat = elem.attrib.get("lat")
        result["geometry"] = "Point:[%s,%s]" % (lon, lat)
    elif objtype == "way":
        result["geometry"] = 'LineString:' + read_way_as_linestring(osm, elem)
    elif objtype == 'relation':
        relation_type = elem.find("tag[@k='type']").attrib.get('v')
        if relation_type not in SUPPORTED_RELATION_TYPES:
            raise OSMRetrievalError(
                'the OSM resource you have tried to import is of type "{}", '
                "which is not supported. Supported relation types are:\n"
                "{}".format(
                    relation_type, ", ".join(sorted(SUPPORTED_RELATION_TYPES))
                )
            )

        ways = []
        # Only filter on waterway types when the relation is a waterway
        # of some sort:
        if relation_type in ("waterway", "watershed"):
            nodes = elem.findall("member[@type='way'][@role='main_stream']")
        else:
            nodes = elem.findall("member[@type='way']")
        if not nodes:
            # If not we look up the `<way>` corresponding to each `<member>`
            # to see if it includes a tag with `k='waterway'` and an element of
            # VALID_WATERWAYS as value.
            for member in elem.findall("member[@type='way']"):
                way = osm.find("way[@id='%s']" % member.get("ref"))
                for waterway in VALID_WATERWAYS:
                    if way.find("tag[@k='waterway'][@v='{waterway}']" .format(waterway=waterway)) is not None:
                        nodes.append(member)
                        break
            if not nodes:
                # In case we found no main_stream <member>s nor any valid waterway tags,
                # we bail out and let the user know
                raise OSMRetrievalError(
                    "cannot import OSM relation: unexpected encoding lacks "
                    "role=main_stream or tag k=waterway v=river")
        for member in nodes:
            way_id = member.attrib.get("ref")
            way = osm.find("way[@id='%s']" % way_id)
            ways.append(read_way_as_linestring(osm, way))
        if not ways:
            # Something went wrong. We don't know what, but we don't want
            # to go on with an empty geometry.
            raise OSMRetrievalError(
                "cannot import OSM relation: no <way>s found")
        result["geometry"] = "MultiLineString:[" + ",".join(ways) + "]"

    return result


class OSMLocationFactory(BrowserView):
    # Makes a location using only an OSM node/way/relation id.
    # Terribly raw at the moment. A mere glance reveals so many places
    # this can fail ungracefully.

    def _fall_back(self, msg):
        show_osm_error(self.context, self.request, msg)

    def __call__(self):
        try:
            objid = str(int(self.request.get('obj')))
            objtype = str(self.request.get('type'))
        except (TypeError, ValueError) as e:
            return self._fall_back(str(e))

        try:
            osm_data = fetch_osm_by_type_and_id(objtype, objid)
        except OSMRetrievalError as e:
            return self._fall_back(str(e))

        ptool = getToolByName(self.context, 'plone_utils')
        repo = getToolByName(self.context, 'portal_repository')
        site = getToolByName(self.context, 'portal_url').getPortalObject()

        title = self.request.get('title') or osm_data.get("tag_name") or "OSM %s %s" % (
            objtype.capitalize(), objid)
        name = ptool.normalizeString(title)

        locid = None
        i = 1
        final_name = name
        while locid is None:
            try:
                locid = self.context.invokeFactory('Location', final_name)
            except BadRequest:
                final_name = name + '-' + str(i)
                i += 1
        try:
            locn = self.context[locid]
            locn.setTitle(title)
            locn.setDescription(u"Location based on OpenStreetMap")
            locn.setGeometry(osm_data["geometry"])
            locn.setInitialProvenance(
                u"OpenStreetMap (%s %s, version %s, "
                u"osm:changeset=%s, %s)" % (
                    objtype.capitalize(),
                    objid,
                    osm_data["version"],
                    osm_data["changeset"],
                    osm_data["timestamp"]
                )
            )
        except Exception as e:
            return self._fall_back(str(e))

        try:
            metadataDoc = site['features']['metadata'][
                'generic-osm-accuracy-assessment']
        except KeyError:
            pass
        else:
            locn.addReference(metadataDoc, 'location_accuracy')

        browse_url = "/".join([OSM_BROWSE, objtype, objid])
        citations = [dict(
            type="citesAsDataSource",
            short_title='OSM',
            citation_detail='{} {}'.format(objtype.title(), objid),
            formatted_citation="osm:%s=%s" % (objtype, objid),
            access_uri=browse_url,
        )]

        field = locn.getField('referenceCitations')
        field.resize(len(citations), locn)
        locn.setReferenceCitations(citations)

        now = DateTime(datetime.datetime.now().isoformat())
        locn.setModificationDate(now)
        repo.save(locn, MESSAGE)
        locn.reindexObject()

        self.request.response.redirect("%s/edit" % locn.absolute_url())


class OSMDateRefresh(BrowserView):
    """Re-fetch the latest OSM data and update the context Location."""

    def __call__(self):
        locn = self.context
        repo = getToolByName(locn, "portal_repository")
        # get first data source referencing OSM, or None:
        data_source = next(
            iter(
                s for s in locn.getReferenceCitations()
                if s.get("type") == "citesAsDataSource"
                and "//www.openstreetmap.org/" in s.get("access_uri", "")
            ),
            None
        )
        if data_source is None:
            IStatusMessage(self.request).addStatusMessage(
                _(
                    "Location has no existing OSM Data Source citation, "
                    "so OSM data cannot be refreshed."
                ),
                type="error"
            )
            self.request.response.redirect(locn.absolute_url())
            return

        objtype, objid = data_source["access_uri"].split("/")[-2:]

        # Get the latest data from the OSM API
        try:
            osm_data = fetch_osm_by_type_and_id(objtype, objid)
        except OSMRetrievalError as e:
            show_osm_error(locn, self.request, str(e))
            return

        # Update the context Location
        locn.setGeometry(osm_data["geometry"])
        locn.setInitialProvenance(
            u"OpenStreetMap (%s %s, version %s, "
            u"osm:changeset=%s, %s)" % (
                objtype.capitalize(),
                objid,
                osm_data["version"],
                osm_data["changeset"],
                osm_data["timestamp"]
            )
        )
        locn.setModificationDate(DateTime(datetime.datetime.now().isoformat()))
        msg = "Reimported full {} geometry and updated provenance".format(objtype)
        repo.save(locn, msg)
        locn.reindexObject()

        IStatusMessage(self.request).addStatusMessage(msg, type="info")
        self.request.response.redirect(locn.absolute_url())
