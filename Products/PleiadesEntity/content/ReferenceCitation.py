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

import logging

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.Field import ObjectField,encode,decode
from Products.Archetypes.Registry import registerField
from Products.Archetypes.utils import DisplayList
from Products.Archetypes import config as atconfig
from Products.Archetypes.Widget import *
from Products.Archetypes.Field  import *
from Products.Archetypes.Schema import Schema
try:
    from Products.generator import i18n
except ImportError:
    from Products.Archetypes.generator import i18n

from Products.PleiadesEntity import config

##code-section module-header #fill in your manual code here
##/code-section module-header

from zope.interface import implements

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin


from Products.CMFCore import permissions

from Products.CompoundField.CompoundField import CompoundField

log = logging.getLogger("PleiadesEntity")

schema = Schema((

    StringField(
        name='identifier',
        default="http://atlantides.org/bibliography/",
        required=1,
        widget=StringField._properties['widget'](
            macro="url_widget",
            label="Reference identifier",
            description="This is a link (URL preferred) or other electronic information system identifier (DOI, ISSN, Handle, etc).",
            label_msgid='PleiadesEntity_label_identifier',
            description_msgid='PleiadesEntity_help_identifier',
            i18n_domain='PleiadesEntity',
        ),
    ),
    StringField(
        name='range',
        required=1,
        widget=StringField._properties['widget'](
            label="Specific citation",
            description="A plain-text AJA style citation (see http://www.ajaonline.org/submissions#4) is preferred for entities with no identifier. A short form is acceptable for those with an identifier.",
            label_msgid='PleiadesEntity_label_range',
            description_msgid='PleiadesEntity_help_range',
            i18n_domain='PleiadesEntity',
        ),
    ),

    StringField(
        name='type',
        vocabulary=[
            ("seeFurther", "See Further"), 
            ("seeAlso", "See Also"), 
            ("citesAsRelated", "Related"),
            ("citesAsEvidence", "Evidence"),
            ("citesAsDataSource", "Data Source"),
            ("cites", "Citation") ],
        default="seeFurther",
        widget=SelectionWidget(
            label="Citation Type",
            description='Places need "See Further" and "See Also" citations. Locations and Names should cite ancient texts or objects as evidence and records in external databases or specific articles as confirmation.',
            label_msgid='PleiadesEntity_label_citationType',
            description_msgid='PleiadesEntity_help_citationType',
            i18n_domain='PleiadesEntity',
        ),
    ),

),
)




class ReferenceCitation(CompoundField):
    """
    """
    ##code-section class-header #fill in your manual code here
    ##/code-section class-header



    _properties = CompoundField._properties.copy()
    _properties.update({
        'type': 'referencecitation',
        ##code-section field-properties #fill in your manual code here
        ##/code-section field-properties

        })

    security  = ClassSecurityInfo()

    schema=schema

    security.declarePrivate('set')
    security.declarePrivate('get')

    def _defaultBibliography(self, instance, value):
        ptool = getToolByName(instance, 'plone_utils')
        r = value.get('range')
        if r:
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
        if not value.get('identifier'):
            default = self._defaultBibliography(instance, value)
            if default:
                value['identifier'] = default
        return value

    def SearchableText(self,):
        return 'foobar'

    def set(self, instance, value, **kwargs):
        return CompoundField.set(self, instance, value, **kwargs)

    def get(self, instance, **kwargs):
        value = CompoundField.get(self, instance, **kwargs)
        if not value.get('identifier'):
            default = self._defaultBibliography(instance, value)
            if default:
                value['identifier'] = default
        return value

registerField(ReferenceCitation,
              title='ReferenceCitation',
              description='')

##code-section module-footer #fill in your manual code here
##/code-section module-footer



