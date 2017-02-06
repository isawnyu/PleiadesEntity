from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.memoize import view

FAKE_USERS = ('auser', 'juser', 'buser', 'euser')
REMOVE_USERS = frozenset(
    ['sgilles', 'admin', 'rtalbert', 'thomase', 'sgillies', 'admin2'])
NAME_MAP = {
    'S. Gillies': 'sgilles',
    'T. Elliot': 'thomase',
}


class CreditTools(BrowserView):
    """Utility methods for byline info"""

    def __init__(self, context, request):
        super(CreditTools, self).__init__(context, request)
        self.mtool = getToolByName(context, 'portal_membership')
        self.catalog = getToolByName(context, 'portal_catalog')

    @view.memoize
    def user_in_byline(self, username=None):
        if username in NAME_MAP:
            un = NAME_MAP[username]
        else:
            un = username
        member = self.mtool.getMemberById(un)
        if member:
            return {"id": member.getId(),
                    "fullname": member.getProperty('fullname')}
        else:
            return {"id": None, "fullname": un}

    @view.memoize
    def fixed_creators(self):
        creators = list(self.context.Creators())
        contributors = set(self.context.Contributors())
        if "sgillies" in creators and ("sgillies" in contributors or
                                       "S. Gillies" in contributors):
            creators.remove("sgillies")
        return creators

    @view.memoize
    def citation_authors(self):
        def _abbrev(a):
            parts = [p.strip() for p in a['fullname'].split(" ", 1)]
            if len(parts) == 2 and len(parts[0]) > 2:
                parts[0] = parts[0][0] + "."
            return " ".join(parts)

        authors = [self.user_in_byline(name) for name in self.fixed_creators()]

        authors[1:] = map(_abbrev, authors[1:])

        parts = [p.strip() for p in authors[0]['fullname'].split(" ", 1)]
        if len(parts) == 2 and len(parts[0]) > 2:
            parts[0] = parts[0][0] + "."
        authors[0] = ", ".join(parts[::-1])  # last + ", " + first

        return ", ".join(authors)

    def formatted_title(self):
        title = self.context.Title()
        ct = self.context.Type().lower()
        if ct in ['place', 'location', 'connection', 'name']:
            return unicode(title, 'utf-8') + ': a Pleiades '+ ct + ' resource'
        else:
            return unicode(title, 'utf-8')

    @view.memoize
    def creators(self):
        """ return list of creator's fullnames
        """
        creators = []
        mt = getToolByName(self.context, 'portal_membership')
        creators_tuple = self.context.listCreators()
        for username in creators_tuple:
            member = mt.getMemberById(username)
            if member is not None:
                creators.append(member.getProperty("fullname"))
            else:
                creators.append(username)
        return creators

    @view.memoize
    def contributors(self):
        """ return list of contributor's fullnames
        """
        contributors = []
        mt = getToolByName(self.context, 'portal_membership')
        contributors_tuple = self.context.listContributors()
        for username in contributors_tuple:
            member = mt.getMemberById(username)
            if member is not None:
                contributors.append(member.getProperty("fullname"))
            else:
                contributors.append(username)
        return contributors

    @view.memoize
    def get_credits(self):
        mtool = self.mtool
        catalog = self.catalog
        getMemberById = mtool.getMemberById

        try:
            contributors = set(catalog.uniqueValuesFor('Contributors'))
        except KeyError:
            contributors = set()
        creators = set(catalog.uniqueValuesFor('Creator'))
        contributors = contributors.union(creators) - REMOVE_USERS

        data = {}
        for user in filter(lambda x: x is not None, map(getMemberById,
                                                        contributors)):
            username = user.getUserName()
            if username in FAKE_USERS:
                continue
            a = len(catalog(Contributors=username, review_state="published"))
            b = len(catalog(Creator=username, review_state="published"))
            if a > 0 or b > 0:
                fullname = user.getUser().getProperty('fullname')
                roles = user.getRoles()
                for r in ['Member', 'Contributor', 'Authenticated']:
                    if r in roles:
                        roles.remove(r)
                roles.append('Member')
                roles = ", ".join(roles[~2:~0]) + (
                    "; " * bool(len(roles) - 1) + roles[-1]
                )
                try:
                    member_folder = self.context.unrestrictedTraverse(
                        "Members/" + username)
                    creation_date = member_folder.CreationDate()
                    start = member_folder.created()
                    start_date = "%s %s %s" % (start.day(), start.Month(),
                                               start.year())
                except:
                    creation_date = ""
                    start_date = ""
                data[fullname] = {
                    'fullname': fullname,
                    'username': username,
                    'roles': roles,
                    'start_date': start_date,
                    'start': creation_date,
                    'count': a + b,
                    'contributed': a,
                    'authored': b,
                    'portrait': mtool.getPersonalPortrait(username).absolute_url()
                }

        keys = data.keys()
        keys.sort()
        return [data[k] for k in keys]
