@set PYTHON=C:\Program Files\Plone 2\Python\python.exe
@set ZOPE_HOME=C:\Program Files\Plone 2\Zope
@set INSTANCE_HOME=C:\Program Files\Plone 2\Data
@set SOFTWARE_HOME=C:\Program Files\Plone 2\Zope\lib\python
@set CONFIG_FILE=C:\Program Files\Plone 2\Data\etc\zope.conf
@set PYTHONPATH=%SOFTWARE_HOME%
@set ZOPE_RUN=C:\Program Files\Plone 2\Zope\lib\python\Zope2\Startup\run.py
@set PATH=%PATH%;C:\Program Files\Plone 2\Python
"%PYTHON%" runalltests.py

