<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0" xmlns:gaz="http://www.unc.edu/awmc/gazetteer/schemata/ns/0.3" >
    <xsl:template name="calc_Description">
        <!-- calculates a description string for tests -->
        <xsl:choose>
            <xsl:when test="local-name(.) = 'geoEntity'"><xsl:call-template name="calc_Description_geoEntity"/></xsl:when>
            <xsl:when test="local-name(.) = 'name'"><xsl:call-template name="calc_Description_name"/></xsl:when>
            <xsl:otherwise>Untrapped local-name() in named template "calc_Description" = "<xsl:value-of select="local-name(.)"/>"</xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="calc_Description_geoEntity">
        <xsl:variable name="geoEntityType"><xsl:value-of select="normalize-space(./gaz:classificationSection[gaz:classificationScheme/gaz:schemeName='geoEntityType']/gaz:classificationTerm)"/></xsl:variable>
        <xsl:variable name="identification">
            <xsl:call-template name="calc_Identification_geoEntity">
                <xsl:with-param name="geoEntityType"><xsl:value-of select="$geoEntityType"/></xsl:with-param>
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="periodization">
            <xsl:call-template name="calc_Periodization_geoEntity">
                <xsl:with-param name="geoEntityType"><xsl:value-of select="$geoEntityType"/></xsl:with-param>
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="localization">
            <xsl:call-template name="calc_Localization_geoEntity">
                <xsl:with-param name="geoEntityType"><xsl:value-of select="$geoEntityType"/></xsl:with-param>
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="nomination">
            <xsl:call-template name="calc_Nomination_geoEntity">
                <xsl:with-param name="geoEntityType"><xsl:value-of select="$geoEntityType"/></xsl:with-param>
            </xsl:call-template>
        </xsl:variable>
        <xsl:value-of select="$identification"/><xsl:value-of select="$periodization"/><xsl:value-of select="$localization"/>.<xsl:if test="string-length($nomination) &gt; 0"><xsl:text> </xsl:text><xsl:value-of select="$nomination"/>.</xsl:if>
    </xsl:template>
    
    <xsl:template name="calc_Identification_geoEntity">
        <xsl:param name="geoEntityType"/>
        <xsl:choose>
            <xsl:when test="$geoEntityType = 'unlocated'">An ancient geographic entity that cannot now be located with certainty</xsl:when>
            <xsl:when test="$geoEntityType = 'false'"><xsl:apply-templates select="//gaz:name[1]/gaz:nameStringTransliterated/text()"/> is a false geographic name<xsl:if test="//gaz:name[1]/gaz:classificationSection/gaz:note"> (<xsl:apply-templates select="//gaz:name[1]/gaz:classificationSection/gaz:note/text()"/>)</xsl:if></xsl:when>
            <xsl:otherwise>An ancient <xsl:value-of select="$geoEntityType"/></xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="calc_Periodization_geoEntity">
        <xsl:param name="geoEntityType"/>
        <xsl:variable name="periodCount"><xsl:value-of select="count(./gaz:timePeriod)"/></xsl:variable>
        <xsl:choose>
            <xsl:when test="$geoEntityType = 'false'"></xsl:when>
            <xsl:when test="$periodCount = 0">, attestation unkown</xsl:when>
            <xsl:when test="$periodCount = 1">, attested during the <xsl:value-of select="./gaz:timePeriod/gaz:timePeriodName"/> period</xsl:when>
            <xsl:otherwise>, attested during the <xsl:for-each select="./gaz:timePeriod"><xsl:value-of select="gaz:timePeriodName"/><xsl:if test="count(following-sibling::gaz:timePeriod) &gt; 1">, </xsl:if><xsl:if test="count(following-sibling::gaz:timePeriod) = 1"> and </xsl:if></xsl:for-each> periods</xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="calc_Localization_geoEntity">
        <xsl:param name="geoEntityType"/>
        <xsl:if test="gaz:modernLocation"><xsl:text> (</xsl:text><xsl:if test="$geoEntityType = 'unlocated'">approximate </xsl:if>modern location: <xsl:apply-templates select="gaz:modernLocation/text()"/>)</xsl:if>
    </xsl:template>
    
    <xsl:template name="calc_Nomination_geoEntity">
        <xsl:param name="geoEntityType"/>
        <xsl:if test="$geoEntityType != 'false'">
            <xsl:variable name="nameCount"><xsl:value-of select="count(//gaz:name)"/></xsl:variable>
            <xsl:choose>
                <xsl:when test= "$nameCount = 0">Its ancient name is not known</xsl:when>
                <xsl:otherwise>It was known in antiquity by the name<xsl:if test="$nameCount &gt; 1">s</xsl:if>: <xsl:for-each select="//gaz:name"><xsl:value-of select="gaz:nameStringTransliterated"/><xsl:if test="count(following-sibling::gaz:name) &gt; 1">, </xsl:if><xsl:if test="count(following-sibling::gaz:name) = 1"> and </xsl:if></xsl:for-each></xsl:otherwise>
            </xsl:choose>
        </xsl:if>
    </xsl:template>
    
    <xsl:template name="calc_Description_name">
        
    </xsl:template>
    
</xsl:stylesheet>
