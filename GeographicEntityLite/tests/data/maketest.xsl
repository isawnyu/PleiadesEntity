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
<!-- checking the title may prove complicated
    &gt;&gt;&gt; from Products.GeographicEntityLite.cooking import setGeoTitleFromNames
    &gt;&gt;&gt; setGeoTitleFromNames(en) 
    'Amblada'
    &gt;&gt;&gt; en.Title()
    'Amblada'
    -->    
    </xsl:template>
    
    <xsl:template match="gaz:ID">
    &gt;&gt;&gt; enID = '<xsl:value-of select="."/>'
    &gt;&gt;&gt; folder.invokeFactory('GeographicEntityLite', id=enID)
    '<xsl:value-of select="."/>'
    &gt;&gt;&gt; en = getattr(folder, enID)
    &gt;&gt;&gt; en.setTitle(enID)
    &gt;&gt;&gt; en.Title()
    '<xsl:value-of select="."/>'
    &gt;&gt;&gt; en.setIdentifier(enID)
    &gt;&gt;&gt; en.getIdentifier()
    '<xsl:value-of select="."/>'
    </xsl:template>
    
    <xsl:template match="gaz:modernLocation">
    &gt;&gt;&gt; en.setModernLocation(u'<xsl:apply-templates />')
    >>> en.getModernLocation()
    '<xsl:apply-templates />'
    </xsl:template>
    
    <xsl:template match="gaz:timePeriod">
        <xsl:if test="count(preceding-sibling::gaz:timePeriod) = 0">
            <xsl:variable name="timestring"><xsl:for-each select="../gaz:timePeriod">'<xsl:value-of select="normalize-space(gaz:timePeriodName)"/>'<xsl:if test="count(following-sibling::gaz:timePeriod) &gt; 0">, </xsl:if></xsl:for-each></xsl:variable>
    &gt;&gt;&gt; en.setTimePeriods([<xsl:value-of select="$timestring"/>])
    &gt;&gt;&gt; en.getTimePeriods()
    (<xsl:value-of select="$timestring"/><xsl:if test="count(../gaz:timePeriod) = 1">,</xsl:if>)
        </xsl:if>
    </xsl:template>
    <!-- note: handling name classification is currently disabled b/c the content type doesn't support it -->
    <xsl:template match="gaz:classificationSection">
        <xsl:if test="local-name(..) != 'name'">
        <xsl:variable name="lame"><xsl:value-of select="descendant::gaz:schemeName"/></xsl:variable>
        <xsl:variable name="camelized"><xsl:value-of select="translate(substring($lame, 1, 1), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/><xsl:value-of select="substring($lame, 2)"/></xsl:variable>
    &gt;&gt;&gt; en<xsl:if test="local-name(..) = 'name'">_name</xsl:if>.set<xsl:value-of select="$camelized"/>('<xsl:value-of select="gaz:classificationTerm"/>')
    &gt;&gt;&gt; en<xsl:if test="local-name(..) = 'name'">_name</xsl:if>.get<xsl:value-of select="$camelized"/>()
    '<xsl:value-of select="gaz:classificationTerm"/>'</xsl:if>
    </xsl:template>
    
    <xsl:template match="gaz:secondaryReferences">
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="tei:bibl">
        <xsl:if test="count(preceding-sibling::tei:bibl) = 0">
            <xsl:variable name="biblstring"><xsl:for-each select="../tei:bibl">u'<xsl:apply-templates/>'<xsl:if test="count(following-sibling::tei:bibl) &gt; 0">, </xsl:if></xsl:for-each></xsl:variable>
    &gt;&gt;&gt; en.setSecondaryReferences([<xsl:value-of select="$biblstring"/>])
    &gt;&gt;&gt; en.getSecondaryReferences()
    (<xsl:value-of select="$biblstring"/>)
        </xsl:if>
    </xsl:template>
    
    <xsl:template match="gaz:spatialLocation">
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="georss:point">
    &gt;&gt;&gt; en.setSpatialCoordinates('<xsl:value-of select="normalize-space(.)"/> 0.0')
    &gt;&gt;&gt; en.getSpatialCoordinates()
    '<xsl:value-of select="normalize-space(.)"/> 0.0'        
    &gt;&gt;&gt; en.setSpatialGeometryType('point')
    &gt;&gt;&gt; en.getSpatialGeometryType()
    'point'        
    </xsl:template>    
    
    <xsl:template match="gaz:name">
        <xsl:variable name="nameid"><xsl:value-of select="/gaz:geoEntity/gaz:ID"/>-n<xsl:value-of select="count(preceding-sibling::gaz:name)+1"/></xsl:variable>
    &gt;&gt;&gt; nameID = '<xsl:value-of select="$nameid"/>'
    &gt;&gt;&gt; en.invokeFactory('GeographicNameLite', id=nameID)
    '<xsl:value-of select="$nameid"/>'
    &gt;&gt;&gt; en_name = getattr(en, nameID)
    &gt;&gt;&gt; en_name.setIdentifier('<xsl:value-of select="$nameid"/>')
    &gt;&gt;&gt; en_name.getIdentifier()
    '<xsl:value-of select="$nameid"/>'
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="gaz:nameString">
    &gt;&gt;&gt; en_name.setNameAttested(u'<xsl:apply-templates />')
    &gt;&gt;&gt; en_name.getNameAttested()
    u'<xsl:apply-templates />'
        <xsl:variable name="language"><xsl:call-template name="getlangstring"><xsl:with-param name="langcode"><xsl:value-of select="@xml:lang"/></xsl:with-param></xsl:call-template></xsl:variable>
    &gt;&gt;&gt; en_name.setNameLanguage('<xsl:value-of select="normalize-space($language)"/>')
    &gt;&gt;&gt; en_name.getNameLanguage()
    <xsl:choose>
    <xsl:when test="contains($language, 'unknown')">''</xsl:when>
    <xsl:otherwise>'<xsl:value-of select="normalize-space($language)"/></xsl:otherwise>
    </xsl:choose>
    </xsl:template>
    
    <xsl:template match="gaz:nameStringTransliterated">
    &gt;&gt;&gt; en_name.setTitle('<xsl:value-of select="."/>')
    &gt;&gt;&gt; en_name.Title()
    '<xsl:value-of select="."/>'
    </xsl:template>
    
    <xsl:template match="*">
    &gt;&gt;&gt; test_msg = 'There is an xml element in the test data that was not handled by the maketest.xsl transformation. Element name = <xsl:value-of select="name(.)"/>'
    &gt;&gt;&gt; print test_msg
    ''
    </xsl:template>
    
    <xsl:template match="text()">
        <xsl:variable name="normedtext"><xsl:value-of select="."/></xsl:variable>
  <xsl:for-each select="string-to-codepoints($normedtext)">
    <xsl:choose>
        <xsl:when test=". = 160"> </xsl:when>  <!-- get rid of non-breaking spaces -->
      <xsl:when test=". > 127">\x<xsl:call-template name="toHex"><xsl:with-param name="decimalNumber"><xsl:value-of select="."/></xsl:with-param></xsl:call-template></xsl:when>
        <xsl:otherwise><xsl:value-of select="codepoints-to-string(.)"/></xsl:otherwise>
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
    
    <!-- The toHex template was written by Peter Doggett. 
          This copy was obtained from http://www.mhonarc.org/archive/html/xsl-list/2003-03/msg01227.html
          on 14 September 2006 -->
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
</xsl:stylesheet>
