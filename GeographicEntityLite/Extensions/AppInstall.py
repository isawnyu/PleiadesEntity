from StringIO import StringIO
from Products.GeographicEntityLite.config import PROJECTNAME
from Products.GeographicEntityLite.AppConfig import VOCABULARIES
import os, sys,logging
from xml.dom.minidom import parse
from Products.PloneLanguageTool import LanguageTool
from Products.CMFCore.utils import getToolByName

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
    desired_languages = {}
    # testing - kill off test languages
    
    # get a reference to the Plone Language Tool so we can access its methods
    ltoolid = LanguageTool.id
    ltool = getToolByName(self, ltoolid, None)
    if ltool is None:
        return None
    ltool.removeLanguage('grc')
    ltool.removeLanguage('grc-Latn')
    ltool.removeLanguage('la-Grek')
    
    
    available_languages = ltool.getAvailableLanguageInformation()
    
    vocabfile = open(vocabfilepath, 'r')
    #vocabdata = vocabfile.read()
    #logger.info('Contents of vocabxmlfile == ' + vocabdata)
    vocabdom = parse(vocabfile)
    
    def getText(nodelist):
        alltext = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                alltext += node.data
            else:
                alltext += getText(node.childNodes)
        return alltext
        
    def handleVdex(vdex):
        terms = vdex.getElementsByTagName("term")
        handleTerms(terms)
        logger.info('in handleVdex')
        
        
    def handleTerms(terms):
        for term in terms:
            handleTerm(term)
            
    def handleTerm(term):
        logger.info('handleTerm = ' + getText(term.childNodes))
        lang_code = getText(term.getElementsByTagName("termIdentifier"))
        logger.info('lang_code = ' + lang_code)
        lang_names = getLangNamesForTerm(term)
        #for lang_name in lang_names:
        #    logger.info('lang_name = ' + lang_name[1] + ' (' + lang_name[0] + ')')
        lang_info = {}
        # english
        # native
        if lang_names.has_key(lang_code):
            lang_info["native"] = lang_names[lang_code]
            logger.info('native = ' + lang_info["native"])
        else:
            lang_info["native"] = '     '
        if lang_names.has_key("en"):
            lang_info["english"] = lang_names["en"]
            logger.info('english = ' + lang_info["english"])
        else:
            lang_info["english"] = '     '
        if available_languages.has_key(lang_code):
            logger.info('this language is already available')
            if available_languages[lang_code]['selected']:
                logger.info('this language is selected as supported')
            else:
                logger.info('this language is not supported by default ... trying to select it')
                ltool.addSupportedLanguage(lang_code)
        else:
            logger.info('this language is not available ... trying to add it')
            ltool.addLanguage(lang_code, lang_info)
            ltool.addSupportedLanguage(lang_code)
            # {code : {native, english, flag}}.
            
            
    def getLangNamesForTerm(term):
        lang_names = {}
        captions = term.getElementsByTagName("caption")
        for langstring in captions[0].getElementsByTagName("langstring"):
            lang_names[langstring.getAttribute("language")] = langstring.childNodes[0].nodeValue
            # lang_names.append((langstring.getAttribute("language"), langstring.childNodes[0].nodeValue))
        return lang_names
        
        
    handleVdex(vocabdom)
    
    # for each term
       # if language-from-term not available from language tool, add it as custom
       # if language-from-term is not selected (supported) in language tool, select it
    logger.warning('Content of vocabxmfile ignored - installer code not finished')
    
    # clean up the dom, now that we are done with it
    vocabdom.unlink()
    
    logger.info('Finished installing languages from ' + vocabfilepath)

        
