@set ZOPE_HOME=C:\Program Files\Plone 2\Zope
@set PYTHON=C:\Program Files\Plone 2\Python\python.exe
@set SOFTWARE_HOME=C:\Program Files\Plone 2\Zope\lib\python
@set INSTANCE_HOME=%SOFTWARE_HOME%
@set CONFIG_FILE=C:\Program Files\Plone 2\Data\etc\zope.conf
@set PYTHONPATH=%SOFTWARE_HOME%
@set TEST_RUN=%ZOPE_HOME%\bin\test.py

"%PYTHON%" "%TEST_RUN%" --usecompiled -vp --config-file="%CONFIG_FILE%" -s Products.PleiadesEntity  
