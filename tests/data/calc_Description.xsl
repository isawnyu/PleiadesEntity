<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0" 
        xmlns:awmcgaz="http://www.unc.edu/awmc/gazetteer/schemata/ns/0.3" 
    xmlns:adlgaz="http://www.alexandria.ucsb.edu/gazetteer/ContentStandard/version3.2/"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:georss="http://www.georss.org/georss"
    xmlns:dc="http://purl.org/dc/elements/1.1/">

    <xsl:template name="calc_Description">
        <!-- calculates a description string for tests -->
        <xsl:variable name="calculatedDescription"><xsl:choose>
            <xsl:when test="local-name(.) = 'geoEntity'"><xsl:call-template name="calc_Description_geoEntity"/></xsl:when>
            <xsl:when test="local-name(.) = 'featureName'"><xsl:call-template name="calc_Description_name"/></xsl:when>
            <xsl:otherwise>Untrapped local-name() in named template "calc_Description" = "<xsl:value-of select="local-name(.)"/>"</xsl:otherwise>
        </xsl:choose></xsl:variable>
        <xsl:value-of select="normalize-space($calculatedDescription)"/></xsl:template>
    
    <xsl:template name="calc_Description_geoEntity">
        <xsl:variable name="geoEntityType"><xsl:value-of select="normalize-space(./adlgaz:classificationSection[adlgaz:classificationScheme/adlgaz:schemeName='geoEntityType']/adlgaz:classificationTerm)"/></xsl:variable>
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
            <xsl:when test="$geoEntityType = 'false'"><xsl:apply-templates select="//adlgaz:featureName[1]/awmcgaz:transliteration/text()"/> is a false geographic name<xsl:if test="//adlgaz:featureName[1]/adlgaz:classificationSection/awmcgaz:note"> (<xsl:apply-templates select="//adlgaz:featureName[1]/adlgaz:classificationSection/awmcgaz:note/text()"/>)</xsl:if></xsl:when>
            <xsl:otherwise>An ancient <xsl:value-of select="$geoEntityType"/></xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="calc_Periodization_geoEntity">
        <xsl:param name="geoEntityType"/>
        <xsl:variable name="periodCount"><xsl:value-of select="count(./adlgaz:timePeriod)"/></xsl:variable>
        <xsl:choose>
            <xsl:when test="$geoEntityType = 'false'"></xsl:when>
            <xsl:when test="$periodCount = 0">, attestation unkown</xsl:when>
            <xsl:when test="$periodCount = 1">, attested during the <xsl:value-of select="./adlgaz:timePeriod/adlgaz:timePeriodName"/> period</xsl:when>
            <xsl:otherwise>, attested during the <xsl:for-each select="./adlgaz:timePeriod"><xsl:value-of select="adlgaz:timePeriodName"/><xsl:if test="count(following-sibling::adlgaz:timePeriod) &gt; 1">, </xsl:if><xsl:if test="count(following-sibling::adlgaz:timePeriod) = 1"> and </xsl:if></xsl:for-each> periods</xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="calc_Localization_geoEntity">
        <xsl:param name="geoEntityType"/>
        <xsl:if test="awmcgaz:modernLocation"><xsl:text> (</xsl:text><xsl:if test="$geoEntityType = 'unlocated'">approximate </xsl:if>modern location: <xsl:apply-templates select="awmcgaz:modernLocation/text()"/>)</xsl:if>
    </xsl:template>
    
    <xsl:template name="calc_Nomination_geoEntity">
        <xsl:param name="geoEntityType"/>
        <xsl:if test="$geoEntityType != 'false'">
            <xsl:variable name="nameCount"><xsl:value-of select="count(//adlgaz:featureName)"/></xsl:variable>
            <xsl:choose>
                <xsl:when test= "$nameCount = 0">Its ancient name is not known</xsl:when>
                <xsl:otherwise>It was known in antiquity by the name<xsl:if test="$nameCount &gt; 1">s</xsl:if>: <xsl:for-each select="//adlgaz:featureName"><xsl:value-of select="awmcgaz:transliteration"/><xsl:if test="count(following-sibling::adlgaz:featureName) &gt; 1">, </xsl:if><xsl:if test="count(following-sibling::adlgaz:featureName) = 1"> and </xsl:if></xsl:for-each></xsl:otherwise>
            </xsl:choose>
        </xsl:if>
    </xsl:template>
    
    <xsl:template name="calc_Description_name">
        <xsl:variable name="geoNameType"><xsl:value-of select="normalize-space(./adlgaz:classificationSection[adlgaz:classificationScheme/adlgaz:schemeName='geoNameType']/adlgaz:classificationTerm)"/></xsl:variable>
        <xsl:variable name="geoEntityType"><xsl:value-of select="/descendant::adlgaz:classificationSection[adlgaz:classificationScheme/adlgaz:schemeName='geoEntityType']/adlgaz:classificationTerm"/></xsl:variable>
        <xsl:variable name="identification">
            <xsl:call-template name="calc_Identification_geoName">
                <xsl:with-param name="geoEntityType"><xsl:value-of select="$geoEntityType"/></xsl:with-param>
                <xsl:with-param name="geoNameType"><xsl:value-of select="$geoNameType"/></xsl:with-param>
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="periodization">
            <xsl:call-template name="calc_Periodization_geoName">
                <xsl:with-param name="geoNameType"><xsl:value-of select="$geoNameType"/></xsl:with-param>
            </xsl:call-template>
        </xsl:variable>
        <xsl:value-of select="$identification"/><xsl:value-of select="$periodization"/>.     
    </xsl:template>
    
    <xsl:template name="calc_Identification_geoName">
        <xsl:param name="geoEntityType"/>
        <xsl:param name="geoNameType"/>
        <xsl:choose>
            <xsl:when test="adlgaz:name">(<xsl:apply-templates select="adlgaz:name/text()"/>): </xsl:when>
        </xsl:choose>
        <xsl:choose>
            <xsl:when test="$geoNameType = 'false'">A false name</xsl:when>
            <xsl:when test="$geoEntityType = 'unlocated'">An ancient name for a geographic entity that cannot now be located with certainty</xsl:when>
            <xsl:otherwise>An ancient <xsl:value-of select="$geoNameType"/> name for a <xsl:value-of select="normalize-space(/descendant::adlgaz:classificationSection[adlgaz:classificationScheme/adlgaz:schemeName='geoEntityType']/adlgaz:classificationTerm)"/></xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="calc_Periodization_geoName">
        <xsl:param name="geoNameType"/>
        <xsl:variable name="periodCount"><xsl:value-of select="count(adlgaz:timePeriod)"/></xsl:variable>
        <xsl:choose>
            <xsl:when test="$periodCount = 1">, attested during the <xsl:value-of select="./adlgaz:timePeriod/adlgaz:timePeriodName"/> period</xsl:when>
            <xsl:when test="$periodCount &gt; 1">, attested during the <xsl:for-each select="./adlgaz:timePeriod"><xsl:value-of select="adlgaz:timePeriodName"/><xsl:if test="count(following-sibling::adlgaz:timePeriod) &gt; 1">, </xsl:if><xsl:if test="count(following-sibling::adlgaz:timePeriod) = 1"> and </xsl:if></xsl:for-each> periods</xsl:when>
            <xsl:otherwise>
                <xsl:variable name="entityPeriodCount"><xsl:value-of select="count(/awmcgaz:geoEntity/adlgaz:timePeriod)"/></xsl:variable>
                <xsl:choose>
                    <xsl:when test="$entityPeriodCount &gt; 0">, attested during the <xsl:for-each select="/awmcgaz:geoEntity/adlgaz:timePeriod"><xsl:value-of select="adlgaz:timePeriodName"/><xsl:if test="count(following-sibling::adlgaz:timePeriod) &gt; 1">, </xsl:if><xsl:if test="count(following-sibling::adlgaz:timePeriod) = 1"> and </xsl:if></xsl:for-each> period<xsl:if test="$entityPeriodCount &gt; 1">s</xsl:if></xsl:when>
                </xsl:choose></xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>
