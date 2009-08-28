# -*- coding: utf-8 -*-
#
# File: TemporalAttestation.py
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

#TemporalAttestation

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
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary

from Products.PleiadesEntity import config

##code-section module-header #fill in your manual code here
##/code-section module-header

from zope.interface import implements

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin



from Products.CompoundField.CompoundField import CompoundField
######CompoundField
schema = Schema((

    StringField(
        name='timePeriod',
        widget=SelectionWidget(
            label="Time period",
            description="Select time period for which this name is attested",
            label_msgid='PleiadesEntity_label_timePeriod',
            description_msgid='PleiadesEntity_help_timePeriod',
            i18n_domain='PleiadesEntity',
        ),
        description="Time period for which this name is attested",
        vocabulary=NamedVocabulary("""time-periods"""),
        enforceVocabulary=1,
        required=1,
    ),
    StringField(
        name='confidence',
        widget=SelectionWidget(
            label="Level of confidence",
            description="Select level of confidence in attestation",
            label_msgid='PleiadesEntity_label_confidence',
            description_msgid='PleiadesEntity_help_confidence',
            i18n_domain='PleiadesEntity',
        ),
        description="Level of confidence in temportal attestation",
        vocabulary=NamedVocabulary("""attestation-confidence"""),
        default="confident",
        enforceVocabulary=1,
    ),

),
)




class TemporalAttestation(CompoundField):
    """
    """
    ##code-section class-header #fill in your manual code here
    ##/code-section class-header



    _properties = CompoundField._properties.copy()
    _properties.update({
        'type': 'temporalattestation',
        ##code-section field-properties #fill in your manual code here
        ##/code-section field-properties

        })

    security  = ClassSecurityInfo()

    schema=schema

    security.declarePrivate('set')
    security.declarePrivate('get')


    def getRaw(self, instance, **kwargs):
        return CompoundField.getRaw(self, instance, **kwargs)

    def set(self, instance, value, **kwargs):
        return CompoundField.set(self, instance, value, **kwargs)

    def get(self, instance, **kwargs):
        return CompoundField.get(self, instance, **kwargs)


registerField(TemporalAttestation,
              title='TemporalAttestation',
              description='')

##code-section module-footer #fill in your manual code here
##/code-section module-footer



