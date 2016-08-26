from Acquisition import aq_parent, aq_inner
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage


class PromoteLocationToPlace(BrowserView):

    def __call__(self):
        location = self.context
        oldPlace = aq_parent(aq_inner(location))

        # Filter references to exclude 'data source' type
        refs = location.getReferenceCitations()
        refs = [ref for ref in refs if ref['type'] != 'citesAsDataSource']

        # Create new place from location
        portal = getToolByName(location, 'portal_url').getPortalObject()
        places = portal['places']
        pid = places.generateUniqueId("Place")
        pid = places.invokeFactory(
            'Place', pid,
            title=location.Title(),
            description=location.Description(),
            creators=location.listCreators(),
            contributors=location.Contributors(),
            rights=location.Rights(),
            subject=location.Subject(),
            placeType=location.getFeatureType(),
            text=location.getRawText(),
        )
        place = places[pid]
        place._renameAfterCreation(check_auto_id=True)
        place.Schema()['referenceCitations'].resize(len(refs))
        place.update(referenceCitations=refs)
        IStatusMessage(self.request).add(
            'Added new place {}'.format('/'.join(place.getPhysicalPath())))

        # Connect place to old place
        unique_id = place.generateUniqueId("Connection")
        new_id = unique_id.split('.')[2]
        while place.has_key(new_id):
            unique_id = place.generateUniqueId("Connection")
            new_id = unique_id.split('.')[2]

        place.invokeFactory('Connection', new_id)
        place[new_id].setConnection([oldPlace.UID()])
        place[new_id].setRelationshipType(['at'])
        
        workflow = getToolByName(self.context, "portal_workflow")
        workflow.doActionFor(place[new_id], 'submit')
        workflow.doActionFor(place[new_id], 'publish')
        place[new_id].reindexObject()

        # Move location to new place
        location = api.content.move(location, place)
        IStatusMessage(self.request).add(
            'Moved location to {}'.format('/'.join(location.getPhysicalPath())))

        # Save revision
        portal.portal_repository.save(place, comment='Migrated from location')

        return self.request.response.redirect(place.absolute_url())
