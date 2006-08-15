from StringIO import StringIO
from Products.GeographicEntityLite.config import PROJECTNAME
from Products.GeographicEntityLite.AppConfig import VOCABULARIES
import os, sys,logging

def install(self):
    installVocabularies(self)
    
def installVocabularies(self):
    logger = logging.getLogger(PROJECTNAME + '.AppInstall.installVocabularies')
    vocabpath = os.path.join(os.environ['INSTANCE_HOME'], 'Products', PROJECTNAME, 'vocabularies')
    logger.info('Installing vocabularies from vocabpath == ' + vocabpath)
    for subdir, identifier in VOCABULARIES:
        logger.info('Installing vocabulary ' + identifier + ' from sub-directory ' + subdir)
        if subdir == 'languages':
            installLanguages(self, os.path.join(vocabpath, subdir, identifier + '.xml'))
        else:
            logger.warning('Ignored vocabulary ' + identifier + ' from sub-directory ' + subdir)
    logger.info('Finished installing vocabularies')
    
def installLanguages(self, vocabfilepath):
    logger = logging.getLogger(PROJECTNAME + '.AppInstall.installLanguages')
    logger.info('Installing languages from ' + vocabfilepath)
    vocabfile = open(vocabfilepath, 'r')
    vocabdata = vocabfile.read()
    logger.info('Contents of vocabxmlfile == ' + vocabdata)
    # for each term
       # if language-from-term not available from language tool, add it as custom
       # if language-from-term is not selected (supported) in language tool, select it
    logger.warning('Content of vocabxmfile ignored - installer code not finished')
    logger.info('Finished installing languages from ' + vocabfilepath)

    
