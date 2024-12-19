import collections
import logging
import requests
from urlparse import urljoin, urlparse

from plone import api as plone_api
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


logger = logging.getLogger(__name__)


class ILinkedDataPortlet(IPortletDataProvider):
    pass


@implementer(ILinkedDataPortlet)
class LinkedDataPortletAssignment(base.Assignment):
    title = u"Linked Data Portlet"
    json_root_url = u"https://raw.githubusercontent.com/isawnyu/pleiades.datasets/refs/heads/main/data/sidebar/"

    def __init__(self):
        pass


def load_domain_to_label_map():
    """Read the list of dicts stored in the registry and convert it
    to a dict mapping domains to labels.

    We use the registry so the mapping can be easily updated via
    the /@@pleiades-settings view on the control panel.
    """
    record_name = (
        "pleiades.vocabularies.interfaces.IPleiadesSettings.link_source_titles_for_urls"
    )
    vocab = plone_api.portal.get_registry_record(name=record_name)

    return {rec["source_domain"]: rec["friendly_label"] for rec in vocab}


def place_id_to_url_path(place_id):
    """Given a Place ID (short name), generate the path to
    a JSON file with related content.
    """
    first_three = list(place_id[:3])
    filename = "{}.json".format(place_id)
    parts = first_three + [filename]
    return "/".join(parts)


def json_to_portlet_data(data):
    """Convert raw JSON to format used by the portlet

    Args:
        data (list): List of features with the format:

        {
            "@id": "https://itiner-e.org/route-segment/32431",
            "type": "Feature",
            "properties": {
                "title": "32431 Fanum Fortunae-Rome",
                "summary": "Conjectured Gaius Flaminius Nepos (220-219 BCE) Main Road (Tabula Peutingeriana, Itinerarium Antonini, Via Flaminia)",
                "reciprocal": False
            },
            "links": [
                {
                    "type": "relatedMatch",
                    "identifier": "https://pleiades.stoa.org/places/100447491"
                },
                etc.
            ]
        }


    Returns:
        dict: Dictionary keyed by source labels, which are based on the
        domain in the @id attribute of the raw JSON input value.
    """
    by_domain = collections.defaultdict(list)
    labels_for_domains = load_domain_to_label_map()
    for record in data:
        url = record["@id"]
        domain = urlparse(url).netloc
        label = labels_for_domains.get(domain, domain)
        portlet_data = {
            u"title": record["properties"]["title"],
            u"summary": record["properties"]["summary"],
            u"url": url,
            u"is_reciprocal": record["properties"].get("reciprocal" or False),
        }
        by_domain[label].append(portlet_data)

    # sort the records under each domain by title
    return {
        label: sorted(records, key=lambda x: x["title"])
        for label, records in by_domain.items()
    }


class LinkedDataPortletRenderer(base.Renderer):

    render = ViewPageTemplateFile("templates/linked_data_portlet.pt")

    @property
    def help_link(self):
        # XXX possible weirdness
        # For urljoin to preserve the portal name, we need to make sure the
        # URL ends with a "/"
        site_root = plone_api.portal.get().absolute_url().rstrip("/") + "/"

        return urljoin(site_root, "help/using-pleiades-data/linked-data-sidebar")

    @property
    def github_data(self):
        """Fetch JSON data describing content related to the context
        Place, and restructure it for display in the portlet.
        """
        resource = place_id_to_url_path(self.context.getId())
        url = urljoin(self.data.json_root_url, resource)
        logger.info("Looking for {}".format(url))
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            logger.info("Found it!")
            result = {
                "source_url": url,
                "links_by_source": json_to_portlet_data(data),
            }
            return result
        except Exception as e:
            logger.info("Didn't find it.")
            return None

    def available(self):
        """Show the portlet only for 'Place' content type."""
        context_type = getattr(self.context, "portal_type", "")
        is_place = context_type == "Place"
        logger.info("Available? {}".format(is_place))
        return is_place


class LinkedDataPortletAddForm(base.NullAddForm):
    """We require no user input, so use a NullAddForm"""

    def create(self):
        return LinkedDataPortletAssignment()


class LinkedDataPortletEditForm(base.EditForm):
    schema = None
    label = u"Edit Linked Data Portlet"
    description = u"This portlet has no editable configuration."
