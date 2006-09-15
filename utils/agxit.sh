#!/bin/sh
PYTHON="/home/sean/pleiades/plone-sites/p1/bin/python"
AGXROOT="/home/sean/pleiades/software/ArchGenXML"
export AGXROOT
"$PYTHON" "$AGXROOT"/ArchGenXML.py --author="Sean Gillies" --author="Tom Elliott" --copyright="Ancient World Mapping Center, University of North Carolina at Chapel Hill, U.S.A." --license=GPL -o ./GeographicEntityLite ./models/geographicEntityLite.xmi

