
from Products.CMFPlone.interfaces import IPloneSiteRoot

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup import profile_registry
from Products.GenericSetup import EXTENSION

BA_MAP_IDS = ['1', '1a'] + [str(n) for n in range(2, 103)]
BA_TABLE_COUNT = 13
BA_ROW_COUNT = 755
BA_ID_MAX = len(BA_MAP_IDS) * BA_TABLE_COUNT * BA_ROW_COUNT

