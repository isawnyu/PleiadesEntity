set PYTHON=c:\Python24\python
set AGXROOT=c:\Programs\ArchGenXML
set SANDBOX=\TomDocs\awmcwork\pleiadesact\svnbox
cd %SANDBOX%
%PYTHON% %AGXROOT%\Archgenxml.py --author="Sean Gillies" --author="Tom Elliott" --copyright="Ancient World Mapping Center, University of North Carolina at Chapel Hill, U.S.A." --license=GPL -o ./PleiadesEntity ./PleiadesEntity/models/PleiadesEntity.xmi


