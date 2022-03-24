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
from pleiades.vocabularies.widget import FilteredSelectionWidget
from Products.Archetypes import atapi
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Schema import Schema
from Products.CompoundField.CompoundField import CompoundField


schema = Schema((

    atapi.StringField(
        name='timePeriod',
        widget=FilteredSelectionWidget(
            label="Time period",
            description="Select the time period to be associated with this resource.",
            label_msgid='PleiadesEntity_label_timePeriod',
            description_msgid='PleiadesEntity_help_timePeriod',
            i18n_domain='PleiadesEntity',
        ),
        description="Time period associated with this resource",
        vocabulary_factory="pleiades.vocabularies.time_periods",
        enforceVocabulary=1,
        required=1,
    ),
    atapi.StringField(
        name='confidence',
        widget=atapi.SelectionWidget(
            label="Level of confidence",
            description="Select level of confidence in attestation",
            label_msgid='PleiadesEntity_label_confidence',
            description_msgid='PleiadesEntity_help_confidence',
            i18n_domain='PleiadesEntity',
            format='radio',
        ),
        description="Level of confidence in temportal attestation",
        vocabulary_factory="pleiades.vocabularies.attestation_confidence",
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
