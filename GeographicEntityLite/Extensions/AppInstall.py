import os

from Globals import package_home
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from Products.CMFCore.utils import getToolByName


def install(self):
    """ install needed vocabularies """
    xmlfilepath = os.path.join(os.environ['INSTANCE_HOME'], 'Products', 'GeographicEntityLite', 'vdex', 'nameLanguages.xml')
    xmlfile = open(xmlfilepath, 'r')
    xmldata = xmlfile.read()
    portal=getToolByName(self,'portal_url').getPortalObject()
    atvm = getToolByName(portal, ATVOCABULARYTOOL)
    atvm.invokeFactory('VdexVocabulary', 'scurvy')
    vocab = atvm['scurvy']
    vocab.importXMLBinding(xmldata)
   
