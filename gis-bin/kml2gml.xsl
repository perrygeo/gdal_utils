<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:gml="http://www.opengis.net/gml" xmlns:wfs="http://www.opengis.net/wfs">

	<xsl:output method="xml" indent="yes" encoding="ISO-8859-1" omit-xml-declaration="no" />

	<xsl:template match="/">
		<wfs:FeatureCollection>			
			<xsl:apply-templates />
		</wfs:FeatureCollection>
	</xsl:template>
	
	<xsl:template match="open" />
	
	<xsl:template match="Placemark">
		<gml:featureMember>
			<myFeature>
				<xsl:apply-templates />
			</myFeature>
		</gml:featureMember>
	</xsl:template>
	
	<xsl:template match="LookAt" />
	<xsl:template match="visibility" />
	<xsl:template match="styleUrl" />
	<xsl:template match="Style" />
	
	<xsl:template match="name">
		<gml:name><xsl:value-of select="." /></gml:name>
	</xsl:template>
	
	<xsl:template match="description">
		<gml:description><xsl:value-of select="." /></gml:description>
	</xsl:template>

	<xsl:template match="Point">
		<gml:Point>
			<xsl:apply-templates />
		</gml:Point>
	</xsl:template>
	
	<xsl:template match="LineString">
		<gml:LineString>
			<xsl:apply-templates />
		</gml:LineString>
	</xsl:template>

	<xsl:template match="Polygon">
		<gml:Polygon>
			<xsl:apply-templates />
		</gml:Polygon>
	</xsl:template>
	
	<xsl:template match="extrude" />
	<xsl:template match="tessellate" />
	<xsl:template match="altitudeMode" />
	
	<xsl:template match="outerBoundaryIs">
		<gml:outerBoundaryIs>
			<xsl:apply-templates />
		</gml:outerBoundaryIs>
	</xsl:template>
	
	<xsl:template match="innerBoundaryIs">
		<gml:innerBoundaryIs>
			<xsl:apply-templates />
		</gml:innerBoundaryIs>
	</xsl:template>
	
	<xsl:template match="LinearRing">
		<gml:LinearRing>
			<xsl:apply-templates />
		</gml:LinearRing>
	</xsl:template>

	<xsl:template match="coordinates">
		<gml:coordinates>
			<xsl:value-of select="." />
		</gml:coordinates>
	</xsl:template>
	
</xsl:stylesheet>