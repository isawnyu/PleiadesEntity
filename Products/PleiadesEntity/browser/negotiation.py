from zope.component import queryMultiAdapter
from Products.Five.browser import BrowserView


VIEW_MAP = {
    'text/html': 'base_view',
    'application/xhtml+xml': 'base_view',
    'application/json': u'@@json',
    'application/javascript': u'@@json',
    'application/x-javascript': u'@@json',
    'text/javascript': u'@@json',
    'aplication/ld+json': u'@@json',
    'application/vnd.geo+json': u'@@json',
    'application/rdf+xml': u'@@rdf',
    'text/turtle': '@@turtle',
    'application/x-turtle': u'@@turtle',
    'application/turtle': u'@@turtle',
    'application/vnd.google-earth.kml+xml': u'@@kml',
    'application/vnd.google-earth.kmz': u'@@kml',
}


class ContentNegotiationView(BrowserView):
    """
    Default view for Pleiades content, looks at HTTP_ACCEPT header to
    determine server response.
    """

    def __call__(self):
        """Check ACCEPT header for known formats/views and render."""
        req = self.request
        res = self.request.response
        res.setHeader('Vary', 'Accept')
        accept = req.environ.get('HTTP_ACCEPT', '').split(',')
        user_preferences = []
        for value in accept:
            parts = value.split(";")
            weight = 1.0
            if len(parts) == 2:
                try:
                    weight = float(parts[1].split("=")[1])
                except:
                    weight = 0.3
            user_preferences.append((weight, parts[0].strip()))
        user_preferences.sort(reverse=True)

        for weight, preferred in user_preferences:
            if preferred in VIEW_MAP:
                view_name = VIEW_MAP[preferred]
                if view_name.startswith('@@'):
                    view_name = view_name[2:]
                    view = queryMultiAdapter((self.context, req),
                                             name=view_name)
                else:
                    view = self.context.restrictedTraverse(view_name, None)
                if view is not None:
                    return view()
            if 'html' in preferred:
                return self.context.restrictedTraverse('base_view')()

        view = self.context.restrictedTraverse("conneg_406_message")
        res.setStatus(406)
        return view(pid=self.context.getId())
