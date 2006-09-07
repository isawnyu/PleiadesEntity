echo off
if (%1)==() echo.ABORTED: no destination name!
if (%1)==() exit /b

echo on
python \Programs\ArchGenXML\Archgenxml.py --author="Sean Gillies" --author="Tom Elliott" --copyright="Ancient World Mapping Center, University of North Carolina at Chapel Hill, U.S.A." --license=GPL -o ./%1 ./models/%1.xmi


