import datetime
import logging
import httplib2
from lxml import etree

from Acquisition import aq_inner, aq_parent
from DateTime import DateTime
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from contentratings.interfaces import IUserRating
from plone.memoize import view
from zope.component import getAdapters, getMultiAdapter

from zgeo.geographer.interfaces import IGeoreferenced
from pleiades.geographer.geo import NotLocatedError
from Products.PleiadesEntity.time import to_ad

MESSAGE = (
    "Location from OSM created by "
    "Products.PleiadesEntity.browser.osm.OSMLocationFactory" )

log = logging.getLogger("Pleiades OSM Client")

OSM_API_ENDPOINT = "http://www.openstreetmap.org/api/0.6"
OSM_BROWSE = "http://www.openstreetmap.org/browse"

class OSMLocationFactory(BrowserView):

    # Makes a location using only an OSM node id.
    # Terribly raw at the moment. A mere glance reveals so many places
    # this can fail ungracefully.

    def _fall_back(self, msg):
        # Redirects back to context with a message
        getToolByName(
            self.context, 'plone_utils' ).addPortalMessage(
                _("Location not created. " + msg.rstrip('.') + ".") )
        self.request.response.redirect(self.context.absolute_url())
        return

    def __call__(self):
        
        try:
            nodeid = str(int(self.request.get('node')))
        except (TypeError, ValueError), e:
            self._fall_back(str(e))
            return

        url = "/".join([OSM_API_ENDPOINT, "node", nodeid])
        h = httplib2.Http()        
        resp, content = h.request(url, "GET")
        
        if not resp['status'] == "200":
            self._fall_back("OSM API response: " + resp['status'])
            return

        osm = etree.fromstring(content)
        node = osm.find('node')
        assert node.attrib.get('id') == nodeid

        version = node.attrib.get("version")
        changeset = node.attrib.get("changeset")
        lon = node.attrib.get("lon")
        lat = node.attrib.get("lat")
        timestamp = node.attrib.get("timestamp")
        tag_name = getattr(
            node.find("tag[@k='name']"), "attrib", {} ).get("v", None)

        ptool = getToolByName(self.context, 'plone_utils')
        mtool = getToolByName(self.context, 'portal_membership')
        repo = getToolByName(self.context, 'portal_repository')
        site = getToolByName(self.context, 'portal_url').getPortalObject()

        title = self.request.get('title') or tag_name or "OSM Node " + nodeid
        name = ptool.normalizeString(title)

        try:
            locid = self.context.invokeFactory(
                'Location',
                name,
                title=title,
                description="Location based on OpenStreetMap",
                geometry="Point:[%s,%s]" % (lon, lat),
                creators=[mtool.getAuthenticatedMember().getUserName()],
                initialProvenance=(
                    "OpenStreetMap (Node %s, version %s, "
                    "osm:changeset=%s, %s)" % (
                        nodeid, version, changeset, timestamp) ))
        except Exception, e:
            self._fall_back(str(e))
            return

        locn = self.context[locid]
        metadataDoc = site['features']['metadata'][
            'generic-osm-accuracy-assessment']
        locn.addReference(metadataDoc, 'location_accuracy')

        browse_url = "/".join([OSM_BROWSE, "node", nodeid])
        citations= [dict(
            identifier=browse_url,
            range="osm:node=%s" % nodeid,
            type="citesAsDataSource" )] 

        field = locn.getField('referenceCitations')
        field.resize(len(citations), locn)
        locn.update(referenceCitations=citations)

        now = DateTime(datetime.datetime.now().isoformat())
        locn.setModificationDate(now)
        repo.save(locn, MESSAGE)

        self.request.response.redirect(
            "%s/edit" % self.context[locid].absolute_url() )

