<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0" 
    xmlns:gaz="http://www.unc.edu/awmc/gazetteer/schemata/ns/0.3" 
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:georss="http://www.georss.org/georss">
    <xsl:output encoding="UTF-8" method="text"/>
    
    <!-- not testing: set description -->
    
    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="gaz:geoEntity">
    &gt;&gt;&gt; folder = self.folder
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="gaz:ID">
    &gt;&gt;&gt; import os
     &gt;&gt;&gt; source_dir = os.path.sep.join([os.environ['SOFTWARE_HOME'], 'Products', 'GeographicEntityLite', 'tests', 'data', '<xsl:value-of select="."/>.xml'])
    &gt;&gt;&gt; from Products.GeographicEntityLite.Extensions.batching import load_entity        
    &gt;&gt;&gt; load_entity(folder, source_dir)
    &gt;&gt;&gt; enID = '<xsl:value-of select="."/>'
    &gt;&gt;&gt; en = getattr(folder, enID)
    &gt;&gt;&gt; en.getIdentifier()
    '<xsl:value-of select="."/>'
    <xsl:variable name="calculatedtitle"><xsl:call-template name="gencombinedtitle"/></xsl:variable>
    &gt;&gt;&gt; finalTitle = en.Title()
     <xsl:variable name="finaltitle"><xsl:call-template name="escapetext"><xsl:with-param name="thetext"><xsl:value-of select="$calculatedtitle"/></xsl:with-param></xsl:call-template></xsl:variable>
    &gt;&gt;&gt; soughtFinalTitle = u'<xsl:value-of select="$finaltitle"/>'
    &gt;&gt;&gt; soughtFinalTitle_utf8 = soughtFinalTitle.encode('utf8')
    &gt;&gt;&gt; finalTitle == soughtFinalTitle_utf8
    True
    &gt;&gt;&gt; finalTitle = en.Title()
    &gt;&gt;&gt; finalTitle == soughtFinalTitle_utf8
    True

    </xsl:template>
    
    <xsl:template match="gaz:modernLocation">
    &gt;&gt;&gt; sourcetext = u'<xsl:apply-templates/>'
    &gt;&gt;&gt; sourcetext_utf8 = sourcetext.encode('utf8')
    &gt;&gt;&gt; resulttext_utf8 = en.getModernLocation()
    &gt;&gt;&gt; resulttext_utf8 == sourcetext_utf8
    True
    &gt;&gt;&gt; resulttext = unicode(resulttext_utf8, 'utf8')
    &gt;&gt;&gt; resulttext == sourcetext
    True
    &gt;&gt;&gt; resulttext == u'<xsl:apply-templates/>'
    True
    </xsl:template>
    
    <xsl:template match="gaz:timePeriod">
        <xsl:if test="count(preceding-sibling::gaz:timePeriod) = 0">
            <xsl:variable name="timestring"><xsl:for-each select="../gaz:timePeriod">'<xsl:value-of select="normalize-space(gaz:timePeriodName)"/>'<xsl:if test="count(following-sibling::gaz:timePeriod) &gt; 0">, </xsl:if></xsl:for-each></xsl:variable>
    &gt;&gt;&gt; sourcelist = [<xsl:value-of select="$timestring"/>]
    &gt;&gt;&gt; results = en<xsl:if test="local-name(..) = 'name'">_name</xsl:if>.getTimePeriods()
    <xsl:for-each select="../gaz:timePeriod">
    &gt;&gt;&gt; results[<xsl:value-of select="count(preceding-sibling::gaz:timePeriod)"/>] == '<xsl:value-of select="normalize-space(gaz:timePeriodName)"/>'
    True
    </xsl:for-each>
            </xsl:if>
    </xsl:template>
    
    <xsl:template match="gaz:classificationSection">
        <!-- <xsl:if test="local-name(..) != 'name'"> -->
        <xsl:variable name="lame"><xsl:value-of select="descendant::gaz:schemeName"/></xsl:variable>
        <xsl:variable name="camelized"><xsl:value-of select="translate(substring($lame, 1, 1), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/><xsl:value-of select="substring($lame, 2)"/></xsl:variable>
    &gt;&gt;&gt; en<xsl:if test="local-name(..) = 'name'">_name</xsl:if>.get<xsl:value-of select="$camelized"/>()
    '<xsl:value-of select="gaz:classificationTerm"/>'<!-- </xsl:if> -->
    </xsl:template>
    
    <xsl:template match="gaz:secondaryReferences">
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="tei:bibl">
        <xsl:if test="count(preceding-sibling::tei:bibl) = 0">
            <xsl:variable name="biblstring"><xsl:for-each select="../tei:bibl">u'<xsl:apply-templates/>'<xsl:if test="count(following-sibling::tei:bibl) &gt; 0">, </xsl:if></xsl:for-each></xsl:variable>
    &gt;&gt;&gt; sourcelist = [<xsl:value-of select="$biblstring"/>]
    &gt;&gt;&gt; resultlist = en<xsl:if test="local-name(../..) = 'name'">_name</xsl:if>.getSecondaryReferences()
    <xsl:for-each select="../tei:bibl">
    &gt;&gt;&gt; resultlist[<xsl:value-of select="count(preceding-sibling::tei:bibl)"/>] == sourcelist[<xsl:value-of select="count(preceding-sibling::tei:bibl)"/>].encode('utf8')
    True
    </xsl:for-each>
        </xsl:if>
    </xsl:template>
    
    <xsl:template match="gaz:spatialLocation">
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="georss:point">
    &gt;&gt;&gt; en.getSpatialCoordinates()
    '<xsl:value-of select="normalize-space(.)"/> 0.0'        
    &gt;&gt;&gt; en.getSpatialGeometryType()
    'point'        
    </xsl:template>    
    
    <xsl:template match="gaz:name">
        <xsl:variable name="nameid"><xsl:value-of select="/gaz:geoEntity/gaz:ID"/>-n<xsl:value-of select="count(preceding-sibling::gaz:name)+1"/></xsl:variable>
    &gt;&gt;&gt; nameID = '<xsl:value-of select="$nameid"/>'
    &gt;&gt;&gt; en_name = getattr(en, nameID)
    &gt;&gt;&gt; en_name.getIdentifier()
    '<xsl:value-of select="$nameid"/>'
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="gaz:nameString">
    &gt;&gt;&gt; sourcetext = u'<xsl:apply-templates/>'
    &gt;&gt;&gt; sourcetext_utf8 = sourcetext.encode('utf8')
    &gt;&gt;&gt; resulttext_utf8 = en_name.getNameAttested()
    &gt;&gt;&gt; resulttext_utf8 == sourcetext_utf8
    True
    &gt;&gt;&gt; resulttext = unicode(resulttext_utf8, 'utf8')
    &gt;&gt;&gt; resulttext == sourcetext
    True
    &gt;&gt;&gt; resulttext == u'<xsl:apply-templates/>'
    True
        
        <xsl:variable name="language"><xsl:call-template name="getlangstring"><xsl:with-param name="langcode"><xsl:value-of select="@xml:lang"/></xsl:with-param></xsl:call-template></xsl:variable>
    &gt;&gt;&gt; en_name.getNameLanguage()
    <xsl:choose>
    <xsl:when test="contains($language, 'unknown')">''</xsl:when>
    <xsl:otherwise>'<xsl:value-of select="normalize-space($language)"/>'</xsl:otherwise>
    </xsl:choose>
    </xsl:template>
    
    <xsl:template match="gaz:nameStringTransliterated">
    &gt;&gt;&gt; en_name.Title()
    '<xsl:value-of select="."/>'
    </xsl:template>
    
    <xsl:template match="*">
    &gt;&gt;&gt; test_msg = 'There is an xml element in the test data that was not handled by the maketest.xsl transformation. Element name = <xsl:value-of select="name(.)"/>'
    &gt;&gt;&gt; print test_msg
    ''
    </xsl:template>
    
    <xsl:template match="text()">
        <xsl:call-template name="escapetext">
            <xsl:with-param name="thetext"><xsl:value-of select="."/></xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    
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
            <xsl:when test="count(//gaz:name) = 0">Unnamed <xsl:value-of select="//gaz:classificationSection[descendant::gaz:schemeName='geoEntityType']/gaz:classificationTerm"/><xsl:if test="//gaz:modernLocation">, modern location: <xsl:value-of select="//gaz:modernLocation"/></xsl:if></xsl:when>
            <xsl:when test="//gaz:name[1]/gaz:classificationSection[/gaz:classificationScheme/gaz:schemeName = 'geoNameType']/gaz:classificationTerm = 'ethnic'">
                <xsl:variable name="namecount"><xsl:value-of select="count(//gaz:name)"/></xsl:variable>
                <xsl:for-each select="//gaz:name"><xsl:value-of select="normalize-space(gaz:nameStringTransliterated)"/><xsl:if test="count(following-sibling::gaz:name) &gt; 0">/</xsl:if></xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
                <xsl:variable name="namecount"><xsl:value-of select="count(//gaz:name[descendant::gaz:classificationTerm != 'ethnic'])"/></xsl:variable>
                <xsl:for-each select="//gaz:name[descendant::gaz:classificationTerm != 'ethnic']"><xsl:value-of select="normalize-space(gaz:nameStringTransliterated)"/><xsl:if test="count(following-sibling::gaz:name[descendant::gaz:classificationTerm != 'ethnic']) &gt; 0">/</xsl:if></xsl:for-each>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>
