#!/bin/sh
#
# Run this script from the directory above your working copy

PYTHON="/usr/bin/python"
AGXROOT="/home/sean/Apps/ArchGenXML"
"$PYTHON" "$AGXROOT"/ArchGenXML.py --author="Sean Gillies" --author="Tom Elliott" --copyright="Ancient World Mapping Center, University of North Carolina at Chapel Hill, U.S.A." --license=GPL -o ./GeographicEntityLite ./GeographicEntityLite/models/geographicEntityLite.xmi

