# -*- coding: utf-8 -*-
#
# File: Temporal.py
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
from pleiades.vocabularies.vocabularies import get_vocabulary
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CompoundField.ArrayField import ArrayField
from Products.CompoundField.CompoundWidget import CompoundWidget
from Products.CompoundField.EnhancedArrayWidget import EnhancedArrayWidget
from Products.PleiadesEntity.content.TemporalAttestation import TemporalAttestation
from Products.PleiadesEntity.time import periodRanges, TimePeriodCmp
from zope.globalrequest import getRequest
from zope.interface import implements
import interfaces

schema = atapi.Schema((

    ArrayField(
        TemporalAttestation(
            name='attestations',
            widget=CompoundWidget(
                label="Time period and confidence level",
                label_msgid='PleiadesEntity_label_attestations',
                i18n_domain='PleiadesEntity',
            ),
            description="Temporal attestations",
            multiValued=True,
        ),

        widget=EnhancedArrayWidget(
            label="Temporal attestations",
            description="Select time period and level of confidence in attestation",
            macro="pleiadesattestationwidget",
            label_msgid='PleiadesEntity_label_array:attestations',
            description_msgid='PleiadesEntity_help_array:attestations',
            i18n_domain='PleiadesEntity',
        ),
        size=0,
    ),

))


Temporal_schema = schema.copy()


class Temporal(BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.ITemporal)

    _at_rename_after_creation = True

    schema = Temporal_schema

    # Methods

    security.declareProtected(permissions.View, 'getSortedTemporalAttestations')
    def getSortedTemporalAttestations(self):
        """
        """
        def _cmp(a, b):
            return TimePeriodCmp(self)(a['timePeriod'], b['timePeriod'])
        return sorted(self.getAttestations(), cmp=_cmp)

    security.declareProtected(permissions.View, 'getTimePeriods')
    def getTimePeriods(self):
        """
        """
        return [a['timePeriod'] for a in self.getSortedTemporalAttestations()]

    # Manually created methods

    security.declareProtected(permissions.View, 'displaySortedTemporalAttestations')
    def displaySortedTemporalAttestations(self):
        """
        """
        def _cmp(a, b):
            return TimePeriodCmp(self)(a['timePeriod'], b['timePeriod'])
        attestations = sorted(self.getAttestations(), cmp=_cmp)
        vocab_t = get_vocabulary('time_periods')
        vocab_c = TemporalAttestation.schema[
            'confidence'].vocabulary.getVocabularyDict(self)
        try:
            return [dict(timePeriod=vocab_t[a['timePeriod']], confidence=vocab_c[a['confidence']]) for a in attestations]
        except KeyError:
            return []

    def confidence_vocab(self):
        return TemporalAttestation.schema[
            'confidence'].vocabulary.getVocabulary(self).getTarget()

    security.declareProtected(permissions.View, 'temporalRange')
    def temporalRange(self, period_ranges=None):
        """Nominal temporal range, not accounting for level of confidence"""
        # cache period ranges on request
        if period_ranges is None:
            request = getRequest()
            if request is not None and hasattr(request, '_period_ranges'):
                period_ranges = request._period_ranges
            else:
                period_ranges = periodRanges(self.period_vocab())
                if request is not None:
                    request._period_ranges = period_ranges

        years = []
        for a in self.getAttestations():
            tp = a['timePeriod']
            if tp:
                years.extend(list(period_ranges[a['timePeriod']]))
        if len(years) >= 2:
            return min(years), max(years)
        else:
            return None
