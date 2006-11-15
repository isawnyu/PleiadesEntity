import os

# Adjust this for your sandbox
ROOT = os.environ['INSTANCE_HOME']

# No need to touch anything below
PRODUCT_NAME = 'PleiadesEntity'
TEST_PACKAGE = "Products.%s.tests" % PRODUCT_NAME
TEST_HOME = os.path.sep.join([ROOT, 'Products', PRODUCT_NAME, 'tests'])
TEST_DATA = os.path.sep.join([TEST_HOME, 'data'])

from Products.PleiadesEntity.Extensions.batching import load_entity, loaden
from Products.PleiadesEntity.Extensions.batching import format_listofstrings
from Products.PleiadesEntity.Extensions.xmlutil import purifyText
from Products.PleiadesEntity.Extensions.cooking import setGeoTitleFromNames

