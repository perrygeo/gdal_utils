#!/usr/local/bin/jython
"""
 Worldwind Java SDK example using Jython.
 Based on the AWT1Up.java demo included with WWJ (by Tom Gaskins).
 
 You must have wwj and jython installed to run this.
   jython wwj_demo.py

 You'll probably have to set two environment vars to get this working:
   export CLASSPATH=/opt/wwj/worldwind.jar
   export LD_LIBRARY_PATH=/opt/wwj:$LD_LIBRARY_PATH

 TO DO:
   - Add event listeners
   - work up support for other formats (via geotools)
   
 Author: Matthew Perry
 License: MIT
 Date: 2007-May-13
"""
import gov.nasa.worldwind as wwj
from gov.nasa.worldwind.geom import Angle, LatLon, Position
from worldwinddemo import StatusBar
import java
import javax
import sys
import os


def buildSimpleShapeLayer():
    layer = wwj.layers.RenderableLayer()

    # Polygon
    originLat = 34
    originLon = -120
    positions = java.util.ArrayList()
    positions.add( LatLon(Angle.fromDegrees(originLat + 5.0), Angle.fromDegrees(originLon + 2.5)))
    positions.add( LatLon(Angle.fromDegrees(originLat + 5.0), Angle.fromDegrees(originLon - 2.5)))
    positions.add( LatLon(Angle.fromDegrees(originLat + 2.5), Angle.fromDegrees(originLon - 5.0)))
    positions.add( LatLon(Angle.fromDegrees(originLat - 2.5), Angle.fromDegrees(originLon - 5.0)))
    positions.add( LatLon(Angle.fromDegrees(originLat - 5.0), Angle.fromDegrees(originLon - 2.5)))
    positions.add( LatLon(Angle.fromDegrees(originLat - 5.0), Angle.fromDegrees(originLon + 2.5)))
    positions.add( LatLon(Angle.fromDegrees(originLat - 2.5), Angle.fromDegrees(originLon + 5.0)))
    positions.add( LatLon(Angle.fromDegrees(originLat + 2.5), Angle.fromDegrees(originLon + 5.0)))
    polygon = SurfacePolygon(positions, java.awt.Color(1.0, 0.11, 0.2, 0.7), java.awt.Color(1.0, 0.0, 0.0, 0.7))
    polygon.setStroke( java.awt.BasicStroke(2.0))
    layer.addRenderable(polygon);

    return layer

def buildIconLayer():
    layer = wwj.layers.IconLayer()
    lat = 34
    lon = -120
    icon = wwj.UserFacingIcon("/opt/wwj/src/images/32x32-icon-nasa.png",
                                   Position( Angle.fromDegrees(lat), Angle.fromDegrees(lon), 0))
    icon.setHighlightScale(1.5)
    icon.setToolTipFont( java.awt.Font('Serif', java.awt.Font.ITALIC, 20) ) 
    icon.setToolTipText("Testing Testing 123");
    icon.setToolTipTextColor(java.awt.Color.blue);
    layer.addIcon(icon);

    return layer


def main():   
    print wwj.Version.getVersion()

    # Set up the worldwind canvas
    wwd = wwj.awt.WorldWindowGLCanvas()
    wwd.setPreferredSize( java.awt.Dimension(800,600) )

    # Set up the status bar
    sb = StatusBar()

    # Start up a new frame, add the wwj components and set size
    f = javax.swing.JFrame()
    f.getContentPane().add(wwd, java.awt.BorderLayout.CENTER);
    f.getContentPane().add(sb, java.awt.BorderLayout.PAGE_END);
    f.pack()
    prefSize = f.getPreferredSize();
    parentLocation = java.awt.Point(0,0)
    parentSize = java.awt.Toolkit.getDefaultToolkit().getScreenSize()
    x = parentLocation.x + (parentSize.width - prefSize.width) / 2
    y = parentLocation.y + (parentSize.height - prefSize.height) / 2
    f.setLocation(x,y)
    f.setResizable(True)

    # Add the worldwind model 
    m = wwj.WorldWind.createConfigurationComponent(wwj.AVKey.MODEL_CLASS_NAME)
    for l in m.getLayers():
        print l.getName(), l.class

    m.getLayers().add( buildSimpleShapeLayer() )
    m.getLayers().add( buildIconLayer() )
    m.setShowWireframeExterior(False)
    m.setShowWireframeExterior(False)
    wwd.setModel(m);
    # make status bar listen for canvas events
    sb.setEventSource(wwd)

    # Make it run
    f.setDefaultCloseOperation(javax.swing.JFrame.EXIT_ON_CLOSE);
    f.setVisible(True);


if __name__ == "__main__":
    main()
