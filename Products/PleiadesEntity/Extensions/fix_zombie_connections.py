import transaction
from zope.component.hooks import setSite
from webdav.Lockable import ResourceLockedError

def fix_up_place(place):
    copies = [a for a in place.objectIds() if 'copy_of_' in a]
    for copy in copies:
        if place[copy].id == copy:
            continue
        original = place[place[copy].id]
        copy_last_change = place[copy].workflow_history['pleiades_entity_workflow'][-1]['time']
        original_last_change = original.workflow_history['pleiades_entity_workflow'][-1]['time']
        copy_version = place[copy].version_id
        original_version = original.version_id
        print place_id, copy, "%s [%d] -> %s [%d] " % (original_last_change, original_version, copy_last_change, copy_version)
        place[copy].id = copy
        try:
            item = place[copy]
            item.unindexObject = lambda: None
            del place[copy]
        except ResourceLockedError:
            continue
        finally:
            del item.unindexObject

def scan_site(site, offset=0):
    n = 0
    places = site.places.objectIds('Place')[offset:]
    for place_id in places:
        place = p.places[place_id]
        copies = [a for a in place.objectIds() if 'copy_of_' in a]
        if copies:
            fix_up_place(place)
        n += 1
        if (n % 1000) == 0:
            transaction.commit()
            print n, '/', len(places)

if __name__ == '__main__':
    p = app.plone
    setSite(p)
    try:
        offset = int(sys.argv[-1])
    except ValueError:
        offset = 0
    scan_site(p.plone, offset)