# -*- coding: utf-8 -*-

from zope.interface import Interface

##code-section HEAD
##/code-section HEAD

class IName(Interface):
    """Marker interface for .Name.Name
    """

class ILocation(Interface):
    """Marker interface for .Location.Location
    """

class ITemporalAttestation(Interface):
    """Marker interface for .TemporalAttestation.TemporalAttestation
    """

class IReference(Interface):
    """Marker interface for .Reference.Reference
    """

class ISecondaryReference(Interface):
    """Marker interface for .SecondaryReference.SecondaryReference
    """

class IPrimaryReference(Interface):
    """Marker interface for .PrimaryReference.PrimaryReference
    """

class IPlacefulAssociation(Interface):
    """Marker interface for .PlacefulAssociation.PlacefulAssociation
    """

class ILocationContainer(Interface):
    """Marker interface for .LocationContainer.LocationContainer
    """

class IPlaceContainer(Interface):
    """Marker interface for .PlaceContainer.PlaceContainer
    """

class IPlace(Interface):
    """Marker interface for .Place.Place
    """

##code-section FOOT
##/code-section FOOT