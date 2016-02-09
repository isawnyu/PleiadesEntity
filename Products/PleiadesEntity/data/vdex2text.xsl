<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet 
    xmlns:v="http://www.imsglobal.org/xsd/imsvdex_v1p0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    version="1.0">
    <xsl:output encoding="UTF-8" method="text"/>
    <xsl:key name="tagsbylang" match="*[@language]" use="@language"/>
    
    
    <xsl:template match="/">
        <xsl:text>identifier|</xsl:text>
        <xsl:for-each select="//*[@language and count(. | key('tagsbylang', @language)[1]) = 1]">
            <xsl:sort select="@language"/>
            <xsl:value-of select="@language"/>|</xsl:for-each>
        <xsl:for-each select="//*[@language and count(. | key('tagsbylang', @language)[1]) = 1]">
            <xsl:sort select="@language"/>
            <xsl:value-of select="@language"/>|</xsl:for-each><xsl:text>
</xsl:text>
        <xsl:apply-templates select="v:vdex/v:term"/>
    </xsl:template>
    
    <xsl:template match="v:term">
        <xsl:value-of select="v:termIdentifier"/>|<xsl:apply-templates select="v:caption"/><xsl:apply-templates select="v:description"/><xsl:text>
</xsl:text>
    </xsl:template>
    
    <xsl:template match="v:caption | v:description">
        <xsl:variable name="contextid"><xsl:value-of select="generate-id(.)"/></xsl:variable>
        <xsl:for-each select="//*[@language and count(. | key('tagsbylang', @language)[1]) = 1]">
            <xsl:sort select="@language"/>
            <xsl:variable name="contextlang"><xsl:value-of select="@language"/></xsl:variable>
            <xsl:apply-templates select="//v:langstring[@language=$contextlang and generate-id(..) = $contextid]"/>|</xsl:for-each>
    </xsl:template>
    
    <xsl:template match="v:langstring"><xsl:value-of select="normalize-space(.)"/></xsl:template>
        
            
    
    <!-- the following template matches and represses all vdex tags that are not explicitly handled by other templates --> 
    <xsl:template match="v:*"/>
</xsl:stylesheet>
