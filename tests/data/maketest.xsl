<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0" 
    xmlns:awmcgaz="http://www.unc.edu/awmc/gazetteer/schemata/ns/0.3" 
    xmlns:adlgaz="http://www.alexandria.ucsb.edu/gazetteer/ContentStandard/version3.2/"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:georss="http://www.georss.org/georss"
    xmlns:dc="http://purl.org/dc/elements/1.1/">
    <xsl:import href="calc_Description.xsl"/>
    <xsl:output encoding="UTF-8" method="text"/>
    
    <!-- =========================================================================== -->
    <!-- ROOT OF GAZETTEER FILE -->
    <!-- =========================================================================== -->
    <xsl:template match="/">
    # test programmatic manipulation of geoEntities and geoNames using data associated with entity ID = <xsl:value-of select="//adlgaz:featureID"/>
    # this set of tests procedes attribute-wise and does not test the load-from-file capabilities; there are other tests for that
        <xsl:apply-templates/>
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- geoEntity:  -->
    <!--    * create a Plone folder -->
    <!--    * handle all subordinate elements -->
    <!--    * programmatic retitling of entity on basis of subordinate names -->
    <!--    * set and retrieve entity description -->
    <!-- =========================================================================== -->
    <xsl:template match="awmcgaz:geoEntity">
    # set up a test folder in which to create the entity and its children
    &gt;&gt;&gt; folder = self.folder
        <xsl:apply-templates/>
    # check to see that programmatic renaming of the entity on the basis of its subordinate names works as expected
    <xsl:variable name="calculatedtitle"><xsl:call-template name="gencombinedtitle"/></xsl:variable>
    &gt;&gt;&gt; finalTitle = setGeoTitleFromNames(en)
     <xsl:variable name="finaltitle"><xsl:call-template name="escapetext"><xsl:with-param name="thetext"><xsl:value-of select="$calculatedtitle"/></xsl:with-param></xsl:call-template></xsl:variable>
    &gt;&gt;&gt; soughtFinalTitle = u'<xsl:value-of select="$finaltitle"/>'
    &gt;&gt;&gt; soughtFinalTitle_utf8 = soughtFinalTitle.encode('utf8')
    &gt;&gt;&gt; finalTitle == soughtFinalTitle_utf8
    True
    &gt;&gt;&gt; finalTitle = en.Title()
    &gt;&gt;&gt; finalTitle == soughtFinalTitle_utf8
    True

    # check to see that we can set and retrieve a description
    &gt;&gt;&gt; soughtDescription = u'<xsl:call-template name="calc_Description"/>'
    &gt;&gt;&gt; en.setDescription(soughtDescription)
    &gt;&gt;&gt; gotDescription = en.Description()
    &gt;&gt;&gt; soughtDescription_utf8 = soughtDescription.encode('utf8')
    &gt;&gt;&gt; soughtDescription_utf8 == gotDescription
    True
    
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- featureID:  -->
    <!--    * create a Plone geographic entity object and check for Plone ID goodness -->
    <!--    * set and retrieve interim title on the entity -->
    <!--    * set and retrieve value of the identifier attribute on the entity -->
    <!-- =========================================================================== -->
    <xsl:template match="adlgaz:featureID">
    # create a geographic entity and verify that we can set and retrieve its Plone id
    &gt;&gt;&gt; enID = '<xsl:value-of select="."/>'
    &gt;&gt;&gt; folder.invokeFactory('Place', id=enID)
    '<xsl:value-of select="."/>'
        
    # get a pointer to the entity, then verify we can set and retrieve its interim title
    &gt;&gt;&gt; en = getattr(folder, enID)
    &gt;&gt;&gt; en.setTitle(enID)
    &gt;&gt;&gt; en.Title()
    '<xsl:value-of select="."/>'
        
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- modernLocation:  -->
    <!--    * set and retrieve value of the modernLocation attribute on the entity -->
    <!-- =========================================================================== -->
    <xsl:template match="awmcgaz:modernLocation">
    # verify that we can set and retrieve the value of the modernLocation attribute
    &gt;&gt;&gt; sourcetext = u'<xsl:apply-templates/>'
    &gt;&gt;&gt; sourcetext_utf8 = sourcetext.encode('utf8')
    &gt;&gt;&gt; en.setModernLocation(sourcetext_utf8)
    &gt;&gt;&gt; resulttext_utf8 = en.getModernLocation()
    &gt;&gt;&gt; resulttext_utf8 == sourcetext_utf8
    True
    &gt;&gt;&gt; resulttext = unicode(resulttext_utf8, 'utf8')
    &gt;&gt;&gt; resulttext == sourcetext
    True
    &gt;&gt;&gt; resulttext == u'<xsl:apply-templates/>'
    True
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- timePeriod:  -->
    <!-- NOTE: this template handles periods for entities *and* for names -->
    <!--    * do nothing UNLESS this is the first sibling in a family of periods -->
    <!--    * build a list of periods and test them against the appropriate entity/name -->
    <!-- =========================================================================== -->
    <xsl:template match="adlgaz:timePeriod">
        <xsl:if test="count(preceding-sibling::adlgaz:timePeriod) = 0">
            <xsl:variable name="timestring"><xsl:for-each select="../adlgaz:timePeriod">'<xsl:value-of select="normalize-space(adlgaz:timePeriodName)"/>'<xsl:if test="count(following-sibling::adlgaz:timePeriod) &gt; 0">, </xsl:if></xsl:for-each></xsl:variable>
    # verify that we can set and retrieve a list of timePeriods 
    &gt;&gt;&gt; sourcelist = [<xsl:value-of select="$timestring"/>]
    &gt;&gt;&gt; en<xsl:if test="local-name(..) = 'featureName'">_name</xsl:if>.setTimePeriods(sourcelist)
    &gt;&gt;&gt; results = en<xsl:if test="local-name(..) = 'featureName'">_name</xsl:if>.getTimePeriods()
    <xsl:for-each select="../adlgaz:timePeriod">
    &gt;&gt;&gt; results[<xsl:value-of select="count(preceding-sibling::adlgaz:timePeriod)"/>] == '<xsl:value-of select="normalize-space(adlgaz:timePeriodName)"/>'
    True
    </xsl:for-each>
            </xsl:if>
    </xsl:template>

    <!-- =========================================================================== -->
    <!-- creator:  -->
    <!-- NOTE: this template handles creators for entities *and* for names -->
    <!--    * do nothing UNLESS this is the first sibling in a family of creators -->
    <!--    * build a list of creators and test them against the appropriate entity/name -->
    <!-- =========================================================================== -->
    <xsl:template match="dc:creator">
        <xsl:param name="forname">no</xsl:param>
        <xsl:if test="count(preceding-sibling::dc:creator) = 0">
            <xsl:variable name="contributorstring">
                <xsl:for-each select="../dc:creator">u'<xsl:apply-templates/>'<xsl:if test="count(following-sibling::dc:creator) &gt; 0">, </xsl:if></xsl:for-each>
            </xsl:variable>
    # verify that we can set and retrieve a list of contributors
    &gt;&gt;&gt; sourcelist = [<xsl:value-of select="$contributorstring"/>]
            <xsl:choose>
                <xsl:when test="$forname='yes'">
    &gt;&gt;&gt; en_name.setCreators(sourcelist)
    &gt;&gt;&gt; results = en_name.Creators()
                </xsl:when>
                <xsl:otherwise>
    &gt;&gt;&gt; en.setCreators(sourcelist)
    &gt;&gt;&gt; results = en.Creators()
                </xsl:otherwise>
            </xsl:choose>
    <xsl:for-each select="../dc:creator">
    &gt;&gt;&gt; results[<xsl:value-of select="count(preceding-sibling::dc:creator)"/>] == u'<xsl:apply-templates/>'
    True
    </xsl:for-each>
        </xsl:if>
    </xsl:template>
    

    <!-- =========================================================================== -->
    <!-- contributor:  -->
    <!-- NOTE: this template handles contributors for entities *and* for names -->
    <!--    * do nothing UNLESS this is the first sibling in a family of contributors -->
    <!--    * build a list of contributors and test them against the appropriate entity/name -->
    <!-- =========================================================================== -->
    <xsl:template match="dc:contributor">
        <xsl:param name="forname">no</xsl:param>
        <xsl:if test="count(preceding-sibling::dc:contributor) = 0">
            <xsl:variable name="contributorstring">
                <xsl:for-each select="../dc:contributor">u'<xsl:apply-templates/>'<xsl:if test="count(following-sibling::dc:contributor) &gt; 0">, </xsl:if></xsl:for-each>
            </xsl:variable>
    # verify that we can set and retrieve a list of contributors
    &gt;&gt;&gt; sourcelist = [<xsl:value-of select="$contributorstring"/>]
            <xsl:choose>
                <xsl:when test="$forname='yes'">
    &gt;&gt;&gt; en_name.setContributors(sourcelist)
    &gt;&gt;&gt; results = en_name.Contributors()
                </xsl:when>
                <xsl:otherwise>
    &gt;&gt;&gt; en.setContributors(sourcelist)
    &gt;&gt;&gt; results = en.Contributors()
                </xsl:otherwise>
            </xsl:choose>
    <xsl:for-each select="../dc:contributor">
    &gt;&gt;&gt; results[<xsl:value-of select="count(preceding-sibling::dc:contributor)"/>] == u'<xsl:apply-templates/>'
    True
    </xsl:for-each>
        </xsl:if>
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- classificationSection:  -->
    <!-- NOTE: this template handles periods for entities *and* for names -->
    <!--    * set the appropriate classification type(s) for the entity/name -->
    <!-- =========================================================================== -->
    <xsl:template match="adlgaz:classificationSection">
        <xsl:variable name="lame"><xsl:value-of select="descendant::adlgaz:schemeName"/></xsl:variable>
        <xsl:variable name="camelized"><xsl:value-of select="translate(substring($lame, 1, 1), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/><xsl:value-of select="substring($lame, 2)"/></xsl:variable>
    # verify that we can set and retrieve the appropriate classification type(s)
    &gt;&gt;&gt; en<xsl:if test="local-name(..) = 'featureName'">_name</xsl:if>.set<xsl:value-of select="$camelized"/>('<xsl:value-of select="adlgaz:classificationTerm"/>')
    &gt;&gt;&gt; en<xsl:if test="local-name(..) = 'featureName'">_name</xsl:if>.get<xsl:value-of select="$camelized"/>()
    '<xsl:value-of select="adlgaz:classificationTerm"/>'
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- secondaryReferences:  -->
    <!-- NOTE: this template implicitly handles secondary references for entities *and* for names -->
    <!--    * pass processing on to subordinate templates -->
    <!-- =========================================================================== -->
    <xsl:template match="awmcgaz:secondaryReferences">
    # verify that we can set and retrieve a list of secondaryReferences
        <xsl:apply-templates/>
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- bibl:  -->
    <!-- NOTE: this template handles bibliographic entries for entities *and* for names -->
    <!--    * do nothing UNLESS this is the first sibling in a family of bibls -->
    <!--    * if this is bibl for a name: -->
    <!--       * if primaryReferences then add to primaryReferences -->
    <!--       * otherwise, assume secondaryReferences and add there -->
    <!--    * otherwise, assume this is for an entity and assume secondary References -->
    <!-- =========================================================================== -->
    <xsl:template match="tei:bibl">
        <xsl:if test="count(preceding-sibling::tei:bibl) = 0">
            <xsl:variable name="biblstring"><xsl:for-each select="../tei:bibl">u'<xsl:apply-templates/>'<xsl:if test="count(following-sibling::tei:bibl) &gt; 0">, </xsl:if></xsl:for-each></xsl:variable>
    &gt;&gt;&gt; sourcelist = [<xsl:value-of select="$biblstring"/>]
            <xsl:choose>
                <xsl:when test="ancestor::adlgaz:featureName">
                    <xsl:choose>
                        <xsl:when test="ancestor::awmcgaz:primaryReferences">
    &gt;&gt;&gt; en_name.setPrimaryReferences(sourcelist)
    &gt;&gt;&gt; resultlist = en_name.getPrimaryReferences()
                        </xsl:when>
                        <xsl:otherwise>
    &gt;&gt;&gt; en_name.setSecondaryReferences(sourcelist)
    &gt;&gt;&gt; resultlist = en_name.getSecondaryReferences()
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:when>
                <xsl:otherwise>
    &gt;&gt;&gt; en.setSecondaryReferences(sourcelist)
    &gt;&gt;&gt; resultlist = en.getSecondaryReferences()
                </xsl:otherwise>
            </xsl:choose>
    <xsl:for-each select="../tei:bibl">
    &gt;&gt;&gt; resultlist[<xsl:value-of select="count(preceding-sibling::tei:bibl)"/>] == sourcelist[<xsl:value-of select="count(preceding-sibling::tei:bibl)"/>].encode('utf8')
    True
    </xsl:for-each>
        </xsl:if>
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- spatialLocation:  -->
    <!--    * pass processing on to subordinate templates -->
    <!-- =========================================================================== -->
    <xsl:template match="adlgaz:spatialLocation">
    # verify that we can set and retrieve the spatialLocation and spatialGeometryType
        <xsl:apply-templates/>
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- point:  -->
    <!--    * verify setting of spatial coordinates -->
    <!--    * verify setting of spatial geometry type primitive -->
    <!-- =========================================================================== -->
    <xsl:template match="georss:point">
    &gt;&gt;&gt; en.setSpatialCoordinates('<xsl:value-of select="normalize-space(.)"/> 0.0')
    &gt;&gt;&gt; en.getSpatialCoordinates()
    '<xsl:value-of select="normalize-space(.)"/> 0.0'        
    &gt;&gt;&gt; en.setSpatialGeometryType('point')
    &gt;&gt;&gt; en.getSpatialGeometryType()
    'point'        
    </xsl:template>    
    
    <!-- =========================================================================== -->
    <!-- featureName:  -->
    <!--    * create a Plone geoname as a child of the entity -->
    <!--    * set and retrieve identifier -->
    <!--    * set and retrieve description -->
    <!--    * process all subordinate nodes -->
    <!--    * write and verify creator data (copied from parent entity) -->
    <!--    * write and verify contributor data (copied from parent entity) -->
    <!--    * write and verify copyright statement (copied from parent entity) -->
    <!-- =========================================================================== -->
    <xsl:template match="adlgaz:featureName">
    # verify that we can set and retrieve all information about the featureName
        <xsl:variable name="nameid"><xsl:value-of select="/awmcgaz:geoEntity/adlgaz:featureID"/>-n<xsl:value-of select="count(preceding-sibling::adlgaz:featureName)+1"/></xsl:variable>

    # create a geographic name and verify that we can set and retrieve its Plone id
    &gt;&gt;&gt; nameID = '<xsl:value-of select="$nameid"/>'
    &gt;&gt;&gt; en.invokeFactory('Name', id=nameID)
    '<xsl:value-of select="$nameid"/>'
    &gt;&gt;&gt; en_name = getattr(en, nameID)
        
     # verify that we can set and retrieve an appropriate value for the description attribute
    &gt;&gt;&gt; soughtDescription = u'<xsl:call-template name="calc_Description"/>'
    &gt;&gt;&gt; en_name.setDescription(soughtDescription)
    &gt;&gt;&gt; gotDescription = en_name.Description()
    &gt;&gt;&gt; soughtDescription_utf8 = soughtDescription.encode('utf8')
    &gt;&gt;&gt; soughtDescription_utf8 == gotDescription
    True
        <xsl:apply-templates/>
        <xsl:apply-templates select="//dc:creator">
            <xsl:with-param name="forname">yes</xsl:with-param>
        </xsl:apply-templates>
        <xsl:apply-templates select="//dc:contributor">
            <xsl:with-param name="forname">yes</xsl:with-param>
        </xsl:apply-templates>
        <xsl:apply-templates select="//dc:rights">
            <xsl:with-param name="forname">yes</xsl:with-param>
        </xsl:apply-templates>
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- name:  -->
    <!-- This is the string that holds, if available, the attested, original-language-and-script -->
    <!-- version of the name -->
    <!--    * set and retrieve the nameAttested attribute -->
    <!--    * set and retrieve the nameLanguage attribute (which is about language and script) -->
    <!-- =========================================================================== -->
    <xsl:template match="adlgaz:name">
    # verify that we can set and retrieve a unicode value for the geographic name's nameAttested attribute
    &gt;&gt;&gt; sourcetext = u'<xsl:apply-templates/>'
    &gt;&gt;&gt; sourcetext_utf8 = sourcetext.encode('utf8')
    &gt;&gt;&gt; en_name.setNameAttested(sourcetext_utf8)
    &gt;&gt;&gt; resulttext_utf8 = en_name.getNameAttested()
    &gt;&gt;&gt; resulttext_utf8 == sourcetext_utf8
    True
    &gt;&gt;&gt; resulttext = unicode(resulttext_utf8, 'utf8')
    &gt;&gt;&gt; resulttext == sourcetext
    True
    &gt;&gt;&gt; resulttext == u'<xsl:apply-templates/>'
    True
        
     <xsl:variable name="language"><xsl:call-template name="getlangstring"><xsl:with-param name="langcode"><xsl:value-of select="@xml:lang"/></xsl:with-param></xsl:call-template></xsl:variable>
    # verify that we can set and retrieve an appropriate value for the nameLanguage attribute
    &gt;&gt;&gt; en_name.setNameLanguage('<xsl:value-of select="normalize-space($language)"/>')
    &gt;&gt;&gt; en_name.getNameLanguage()
    <xsl:choose>
    <xsl:when test="contains($language, 'unknown')">''</xsl:when>
    <xsl:otherwise>'<xsl:value-of select="normalize-space($language)"/>'</xsl:otherwise>
    </xsl:choose>
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- transliteration:  -->
    <!-- This is the string that holds an ASCII-transliterated version of the attested name -->
    <!--    * set and retrieve the Plone Title (we're using that field for this purpose -->
    <!-- =========================================================================== -->
    <xsl:template match="awmcgaz:transliteration">

    # verify that we can set and retrieve an appropriate value for the name's title attribute (which should be an ASCII transliteration of the nameAttested value)        
    &gt;&gt;&gt; en_name.setTitle('<xsl:value-of select="."/>')
    &gt;&gt;&gt; en_name.Title()
    '<xsl:value-of select="."/>'
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- rights:  -->
    <!--    * escape, then set and retrieve the rights field -->
    <!-- =========================================================================== -->
    <xsl:template match="dc:rights">
        <xsl:param name="forname">no</xsl:param>
        <xsl:variable name="cleanrights">
            <xsl:for-each select="string-to-codepoints(.)">
                <xsl:choose>
                    <xsl:when test=". = 13 or . = 10 or . = 39"><xsl:call-template name="genpythouniesc">
                            <xsl:with-param name="codepoint-decimal"><xsl:value-of select="."/></xsl:with-param>
                        </xsl:call-template></xsl:when>
                    <xsl:when test=". &lt; 128"><xsl:value-of select="codepoints-to-string(.)"/></xsl:when>
                    <xsl:when test=". = 160"><xsl:text> </xsl:text></xsl:when>  <!-- get rid of non-breaking spaces -->
                    <xsl:otherwise>
                        <xsl:call-template name="genpythouniesc">
                            <xsl:with-param name="codepoint-decimal"><xsl:value-of select="."/></xsl:with-param>
                        </xsl:call-template>
                    </xsl:otherwise>
                </xsl:choose>
                
            </xsl:for-each>
        </xsl:variable>
    # verify that we can set and retrieve an appropriate value for the rights attribute
    &gt;&gt;&gt; sourcetext = u'<xsl:value-of select="normalize-space($cleanrights)"/>'
    &gt;&gt;&gt; sourcetext_utf8 = sourcetext.encode('utf8')
        <xsl:choose>
            <xsl:when test="$forname='yes'">
    &gt;&gt;&gt; en_name.setRights(sourcetext_utf8)
    &gt;&gt;&gt; resulttext_utf8 = en_name.Rights()
            </xsl:when>
            <xsl:otherwise>
    &gt;&gt;&gt; en.setRights(sourcetext_utf8)
    &gt;&gt;&gt; resulttext_utf8 = en.Rights()
            </xsl:otherwise>
        </xsl:choose>
    &gt;&gt;&gt; resulttext_utf8 == sourcetext_utf8
    True
    &gt;&gt;&gt; resulttext = unicode(resulttext_utf8, 'utf8')
    &gt;&gt;&gt; resulttext == sourcetext
    True
    &gt;&gt;&gt; resulttext == u'<xsl:value-of select="normalize-space($cleanrights)"/>'
    True
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- *:  (all other elements) -->
    <!--  Issue a test-breaking alert message if there is an element in the source file that is -->
    <!-- not explicitly trapped by this stylesheet -->
    <!-- =========================================================================== -->
    <xsl:template match="*">
    &gt;&gt;&gt; test_msg = 'There is an xml element in the test data that was not handled by the maketest.xsl transformation. Element name = <xsl:value-of select="name(.)"/>'
    &gt;&gt;&gt; print test_msg
    ''
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- text() -->
    <!-- Pump contents of all text nodes through a named template designed to escape -->
    <!-- characters above Latin-1 so python doctests don't explode in flames -->
    <!-- =========================================================================== -->
    <xsl:template match="text()">
        <xsl:call-template name="escapetext">
            <xsl:with-param name="thetext"><xsl:value-of select="."/></xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    
    <!-- =========================================================================== -->
    <!-- NAMED TEMPLATE: escapetext -->
    <!-- Massage contents of the "thetext" paramater in order to escape -->
    <!-- characters above Latin-1 so python doctests don't explode in flames -->
    <!-- Also: trap for non-breaking space in input stream and replace with regular space -->
    <!-- =========================================================================== -->
    <xsl:template name="escapetext">
        <xsl:param name="thetext"/>
        <xsl:variable name="normedtext"><xsl:value-of select="normalize-space($thetext)"/></xsl:variable>
  <xsl:for-each select="string-to-codepoints($normedtext)">
        <xsl:choose>
            <xsl:when test=". &lt; 128"><xsl:value-of select="codepoints-to-string(.)"/></xsl:when>
            <xsl:when test=". = 160"><xsl:text> </xsl:text></xsl:when>  <!-- get rid of non-breaking spaces -->
            <xsl:otherwise>
                <xsl:call-template name="genpythouniesc">
                    <xsl:with-param name="codepoint-decimal"><xsl:value-of select="."/></xsl:with-param>
                </xsl:call-template>
            </xsl:otherwise>
        </xsl:choose>
  </xsl:for-each>
    </xsl:template>
    
    <xsl:template name="getlangstring">
        <xsl:param name="langcode"/>
        <xsl:choose>
            <xsl:when test="$langcode='grc'">Ancient Greek</xsl:when>
            <xsl:when test="$langcode='la'">Latin</xsl:when>
            <xsl:when test="$langcode='grc-Latn'">Ancient Greek in Latin characters</xsl:when>
            <xsl:when test="$langcode='la-Grek'">Latin in Ancient Greek characters</xsl:when>
            <xsl:otherwise>unknown</xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="genpythouniesc">
        <xsl:param name="codepoint-decimal"/>
        <xsl:variable name="codepoint-hex">
            <xsl:call-template name="toHex">
                <xsl:with-param name="decimalNumber"><xsl:value-of select="$codepoint-decimal"/></xsl:with-param>
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="hexlen"><xsl:value-of select="string-length(string($codepoint-hex))"/></xsl:variable>
        <xsl:text>\U</xsl:text><xsl:value-of select="concat(substring('00000000', 1, 8-$hexlen), string($codepoint-hex))"/>
    </xsl:template>
    <!-- The toHex template was written by Peter Doggett. 
          This copy was obtained from http://www.mhonarc.org/archive/html/xsl-list/2003-03/msg01227.html
          on 14 September 2006  -->
    <xsl:variable name="hexDigits" select="'0123456789ABCDEF'" />
        <xsl:template name="toHex">
            <xsl:param name="decimalNumber" />
            <xsl:if test="$decimalNumber >= 16">
              <xsl:call-template name="toHex">
                <xsl:with-param name="decimalNumber" 
            select="floor($decimalNumber div 16)" />
              </xsl:call-template>
            </xsl:if>
            <xsl:value-of select="substring($hexDigits, 
            ($decimalNumber mod 16) + 1, 1)" />
        </xsl:template>
    
    <xsl:template name="gencombinedtitle">
        <xsl:choose>
            <xsl:when test="count(//adlgaz:featureName) = 0">Unnamed <xsl:value-of select="//adlgaz:classificationSection[descendant::adlgaz:schemeName='geoEntityType']/adlgaz:classificationTerm"/><xsl:if test="//awmcgaz:modernLocation">, modern location: <xsl:value-of select="//awmcgaz:modernLocation"/></xsl:if></xsl:when>
            <xsl:when test="//adlgaz:featureName[1]/adlgaz:classificationSection[/adlgaz:classificationScheme/adlgaz:schemeName = 'geoNameType']/adlgaz:classificationTerm = 'ethnic'">
                <xsl:variable name="namecount"><xsl:value-of select="count(//adlgaz:featureName)"/></xsl:variable>
                <xsl:for-each select="//adlgaz:featureName"><xsl:value-of select="normalize-space(awmcgaz:transliteration)"/><xsl:if test="count(following-sibling::adlgaz:featureName) &gt; 0">/</xsl:if></xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
                <xsl:variable name="namecount"><xsl:value-of select="count(//adlgaz:featureName[descendant::adlgaz:classificationTerm != 'ethnic'])"/></xsl:variable>
                <xsl:for-each select="//adlgaz:featureName[descendant::adlgaz:classificationTerm != 'ethnic']"><xsl:value-of select="normalize-space(awmcgaz:transliteration)"/><xsl:if test="count(following-sibling::adlgaz:featureName[descendant::adlgaz:classificationTerm != 'ethnic']) &gt; 0">/</xsl:if></xsl:for-each>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>
