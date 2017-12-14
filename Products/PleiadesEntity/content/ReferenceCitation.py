# -*- coding: utf-8 -*-
#
# File: ReferenceCitation.py
#
# Copyright (c) 2009 by Ancient World Mapping Center, University of North
# Carolina at Chapel Hill, U.S.A.
# Generator: ArchGenXML Version 2.4.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Sean Gillies <unknown>, Tom Elliott <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Field import *
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import *
from Products.CMFCore.utils import getToolByName
from Products.CompoundField.CompoundField import CompoundField
import logging

log = logging.getLogger("PleiadesEntity")

schema = Schema((

    StringField(
        name='type',
        vocabulary=[
            ("seeFurther", "See Further"),
            ("seeAlso", "See Also"),
            ("citesAsRelated", "Related"),
            ("citesAsEvidence", "Evidence"),
            ("citesAsDataSource", "Data Source"),
            ("cites", "Citation"),
        ],
        default="seeFurther",
        widget=SelectionWidget(
            label="Citation Type",
            description='Pick a keyword/phrase from the list to '
                'indicate the purpose and function of this reference. '
                'See <a '
                'href="https://pleiades.stoa.org/help/citation-types">'
                'Citation Types documentation</a> for definitions of these '
                'terms.',
            label_msgid='PleiadesEntity_label_citationType',
            description_msgid='PleiadesEntity_help_citationType',
            i18n_domain='PleiadesEntity',
        ),
    ),

    StringField(
        name='short_title',
        required=False,
        widget=StringField._properties['widget'](
            label="Short Title",
            description='Enter an "author year" short title or standard '
                'abbreviation for the work being cited. This short title '
                'must match what is found in the <a '
                'href="https://www.zotero.org/groups/2533/pleiades">Pleiades '
                'Zotero Library</a> for the work in question.',
            size=40,
            label_msgid='PleiadesEntity_label_short_title',
            description_msgid='PleiadesEntity_help_short_title',
            i18n_domain='PleiadesEntity',
        ),
    ),

    StringField(
        name='citation_detail',
        required=False,
        widget=StringField._properties['widget'](
            label="Citation Detail",
            description='Enter appropriate additional information when a '
                'subsection of the work is being cited (e.g., page range, '
                'section title, item number, headword, or web page title in '
                'a larger site).',
            size=40,
            label_msgid='PleiadesEntity_label_citation_detail',
            description_msgid='PleiadesEntity_help_citation_detail',
            i18n_domain='PleiadesEntity',
        ),
    ),

    StringField(
        name='formatted_citation',
        required=False,
        widget=StringField._properties['widget'](
            label="Formatted Citation",
            description='Enter a clear, complete, and human-readable '
                'bibliographic citation for the work and section cited as '
                'one might expect to find in a traditional, printed '
                'scholarly bibliography. See further the <a '
                'href="https://pleiades.stoa.org/help/citation-guide/'
                'citation-guide#general_rules_for_references">Pleiades '
                'Citation Guide, sub "General Rules for References."</a>',
            size=79,
            label_msgid='PleiadesEntity_label_formatted_citation',
            description_msgid='PleiadesEntity_help_formatted_citation',
            i18n_domain='PleiadesEntity',
        ),
    ),

    StringField(
        name='bibliographic_uri',
        required=False,
        validators=('isURL',),
        widget=StringField._properties['widget'](
            macro="url_widget",
            label="Bibliographic URI",
            description="This is a URI to an online bibliographic reference (e.g. zotero, worldcat, openlibrary, ...).",
            size=79,
            label_msgid='PleiadesEntity_label_bibliographic_uri',
            description_msgid='PleiadesEntity_help_bibliographic_uri',
            i18n_domain='PleiadesEntity',
        ),
    ),

    StringField(
        name='access_uri',
        required=False,
        validators=('isURL',),
        widget=StringField._properties['widget'](
            macro="url_widget",
            label="Access URI",
            size=79,
            description="This is a URI to access the identified resource.",
            label_msgid='PleiadesEntity_label_access_uri',
            description_msgid='PleiadesEntity_help_access_uri',
            i18n_domain='PleiadesEntity',
        ),
    ),

    StringField(
        name='alternate_uri',
        required=False,
        validators=('isURL',),
        widget=StringField._properties['widget'](
            macro="url_widget",
            label="Alternate URI",
            size=79,
            description="This is an alternate URL for the identified resource",
            label_msgid='PleiadesEntity_label_alternate_uri',
            description_msgid='PleiadesEntity_help_alternate_uri',
            i18n_domain='PleiadesEntity',
        ),
    ),

    StringField(
        name='identifier',
        required=False,
        widget=StringField._properties['widget'](
            macro="url_widget",
            label="Other identifier",
            description="This is an optional non-URL identifier (e.g. DOI, ISSN, Handle, etc).",
            size=40,
            label_msgid='PleiadesEntity_label_other_identifier',
            description_msgid='PleiadesEntity_help_other_identifier',
            i18n_domain='PleiadesEntity',
        ),
    ),
))


class ReferenceCitation(CompoundField):
    _properties = CompoundField._properties.copy()
    _properties.update({
        'type': 'referencecitation',
    })

    schema = schema

    security = ClassSecurityInfo()
    security.declarePrivate('set')
    security.declarePrivate('get')

    def _defaultBibliography(self, instance, value):
        ptool = getToolByName(instance, 'plone_utils')
        r = (value.get('short_title', '') or
             value.get('formatted_citation', '') or value.get('range', ''))
        if r.strip():
            try:
                return "".join([
                    "http://atlantides.org/bibliography/",
                    ptool.normalizeString(r)[0],
                    '.html#',
                    r.split(',')[0].strip().replace(' ', '-')])
            except UnicodeDecodeError:
                log.exception("UnicodeDecodeError in default biblio")
                return ""
        else:
            return ""

    def getRaw(self, instance, **kwargs):
        value = CompoundField.getRaw(self, instance, **kwargs)
        if (not value.get('bibliographic_uri') and not value.get('access_uri')
                and not value.get('identifier')):
            default = self._defaultBibliography(instance, value)
            if default:
                value['bibliographic_uri'] = default
        return value

    def SearchableText(self):
        value = CompoundField.get(self, instance, **kwargs)
        return value.get('short_title', '') + ' ' + value.get('citation_detail', '')

    def set(self, instance, value, **kwargs):
        return CompoundField.set(self, instance, value, **kwargs)

    def get(self, instance, **kwargs):
        value = CompoundField.get(self, instance, **kwargs)
        if (not value.get('bibliographic_uri') and not value.get('access_uri')
                and not value.get('identifier')):
            default = self._defaultBibliography(instance, value)
            if default:
                value['bibliographic_uri'] = default
        return value

registerField(ReferenceCitation, title='ReferenceCitation', description='')
