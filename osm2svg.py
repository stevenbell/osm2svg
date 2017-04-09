# This treats lat/lon as ... (i.e., web map projection)

from IPython import embed
from lxml import etree
import json

# Setup - edit these configuration variables as necessary
inputFile = 'map.osm'
outputFile = 'out.svg'
outWidth = 1000 # Width of the output, in pixels
# The height will be calculated automatically based on the aspect ratio of the
# downloaded chunk of OSM data.

# Load the OSM file
document = etree.parse(open(inputFile))

# Get the bounds of the OSM rectangle, and use this to calculate the scaling
# factors to convert
boundsElems = document.findall('bounds')
if len(boundsElems) is not 1:
  print "Expected exactly one <bounds/> element.  Something is weird."
  exit()

b = boundsElems[0]
minlat = float(b.get('minlat'))
maxlat = float(b.get('maxlat'))
minlon = float(b.get('minlon'))
maxlon = float(b.get('maxlon'))

scale = outWidth / (maxlon - minlon) # Multiply to convert lat/lon to pixels
outHeight = scale * (maxlat - minlat)

# Print the header of the SVG file
out = open(outputFile, 'w')

out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
out.write('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%d" height="%d" viewBox="0 0 %d %d" version="1.1">\n' % (outWidth, outHeight, outWidth, outHeight))


for way in document.findall('way'):
  style = None

  for tag in way.findall('tag'):
    if tag.get('k') == 'highway':
      style = 'stroke="orange" fill="none" stroke-width="3"'
    elif tag.get('k') == 'building':
      style = 'stroke="red" fill="red" stroke-width="1"'
    #print "%s %s" % (tag.get('k'), tag.get('v'))

  # If there is no assigned style, skip this way completely
  if style is None:
    continue

  points = ''
  for noderef in way.findall('nd'):
    nodematch = document.xpath('//node[@id=' + noderef.get('ref') + ']')
    if len(nodematch) is 1:
      lat = float(nodematch[0].get('lat'))
      lon = float(nodematch[0].get('lon'))
      points += '%f %f ' % ((lon - minlon)*scale, (lat-minlat)*scale)
    else:
      print "Error finding node %s for way %s" % (noderef.get('ref'), way.get('id'))
      
  out.write('<polyline points="%s" %s/>\n' % (points, style))

out.write('</svg>')

# For each key

