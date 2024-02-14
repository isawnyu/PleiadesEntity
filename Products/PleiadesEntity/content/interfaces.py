# -*- coding: utf-8 -*-

from zope.interface import Interface

##code-section HEAD
##/code-section HEAD


class IHasDefaultWorks(Interface):
    """Marker interface for content types that need `pleiades_default_works`
    """

class IName(IHasDefaultWorks):
    """Marker interface for .Name.Name
    """

class ILocation(IHasDefaultWorks):
    """Marker interface for .Location.Location
    """

class IConnection(IHasDefaultWorks):
    """Marker interface for .Location.Location
    """

class IFeature(Interface):
    """Marker interface for .Feature.Feature
    """

class IPlaceContainer(Interface):
    """Marker interface for .PlaceContainer.PlaceContainer
    """

class IPlace(Interface):
    """Marker interface for .Place.Place
    """

class IFeatureContainer(Interface):
    """Marker interface for .FeatureContainer.FeatureContainer
    """

class IPositionalAccuracy(Interface):
    """Marker interface for .PositionalAccuracy.PositionalAccuracy
    """

class IWork(Interface):
    """Marker interface for .Work.Work
    """

class INamed(IHasDefaultWorks):
    """Marker interface for .Named.Named
    """

class ITemporal(Interface):
    """Marker interface for .Temporal.Temporal
    """

##code-section FOOT
##/code-section FOOT