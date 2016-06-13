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

from AccessControl import ClassSecurityInfo
from pleiades.vocabularies.widget import TimePeriodSelectionWidget
from Products.Archetypes.Field import *
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import *
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.CompoundField.CompoundField import CompoundField


schema = Schema((

    StringField(
        name='timePeriod',
        widget=TimePeriodSelectionWidget(
            label="Time period",
            description="Select time period for which this name is attested",
            label_msgid='PleiadesEntity_label_timePeriod',
            description_msgid='PleiadesEntity_help_timePeriod',
            i18n_domain='PleiadesEntity',
        ),
        description="Time period for which this name is attested",
        vocabulary_factory="pleiades.vocabularies.time_periods",
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

))


class TemporalAttestation(CompoundField):
    _properties = CompoundField._properties.copy()
    _properties.update({
        'type': 'temporalattestation',
        })

    schema = schema

    security = ClassSecurityInfo()
    security.declarePrivate('set')
    security.declarePrivate('get')

    def getRaw(self, instance, **kwargs):
        return CompoundField.getRaw(self, instance, **kwargs)

    def set(self, instance, value, **kwargs):
        return CompoundField.set(self, instance, value, **kwargs)

    def get(self, instance, **kwargs):
        return CompoundField.get(self, instance, **kwargs)


registerField(TemporalAttestation, title='TemporalAttestation', description='')
