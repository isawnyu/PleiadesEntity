from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.memoize import view

FAKE_USERS = ('auser', 'juser')
REMOVE_USERS = frozenset(['sgilles', 'admin', 'rtalbert', 'thomase'])
NAME_MAP = {
    'sgilles': 'S. Gillies',
    'thomase': 'T. Elliot'
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

    @view.memoize
    def get_credits(self):
        mtool = self.mtool
        catalog = self.catalog

        contributors = set(catalog.uniqueValuesFor('Contributors'))
        creators = set(catalog.uniqueValuesFor('Creator'))
        contributors = contributors.union(creators) - REMOVE_USERS

        data = {}
        for user in filter(lambda x: x is not None, map(mtool.getMemberById,
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
                    creation_date = self.context.restrictedTraverse(
                        "/plone/Members/" + username).CreationDate()
                    start = DateTime.DateTime(creation_date)
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
