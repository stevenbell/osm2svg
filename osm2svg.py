# This treats lat/lon as ... (i.e., web map projection)

from IPython import embed
from lxml import etree
import json

# Setup - edit these configuration variables as necessary
inputFile = 'map.osm'
styleFile = 'styles.json'
outputFile = 'out.svg'
outWidth = 1000 # Width of the output, in pixels
# The height will be calculated automatically based on the aspect ratio of the
# downloaded chunk of OSM data.

def __main__():
  # Load the style file
  styleDef = json.load(open(styleFile))
  styles = {}
  for tag,attrs in styleDef.items():
    styles[tag] = ' '.join(["%s=\"%s\"" %(k,str(v)) for k,v in attrs.items()])

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
  
  # Load all the datapoints into memory
  # This will let us do (relatively) fast lookups when rendering, rather than
  # xpath calls every time we need another point
  nodes = {}
  for node in document.findall('node'):
    nodes[node.get('id')] = (node.get('lon'), node.get('lat'))

  # Print the header of the SVG file
  out = open(outputFile, 'w')
  
  out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
  out.write('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%d" height="%d" viewBox="0 0 %d %d" version="1.1">\n' % (outWidth, outHeight, outWidth, outHeight))
  
  
  for way in document.findall('way'):
    style = None
  
    for tag in way.findall('tag'):
      searchtag = tag.get('k') + '.' + tag.get('v')
      if searchtag in styles: # search for key.value in styles
        style = styles[searchtag]
        break # Found a style, quit right away
      elif tag.get('k') in styles: # failed, just search for key
        style = styles[tag.get('k')]
        break # Found a style, quit right away
 
    # If there is no assigned style, skip this way completely
    if style is None:
      continue
  
    points = ''
    for noderef in way.findall('nd'):
      nodeid = noderef.get('ref')
      if nodeid in nodes:
        lon = float(nodes[nodeid][0])
        lat = float(nodes[nodeid][1])
        points += '%f %f ' % ((lon - minlon)*scale, (lat-minlat)*scale)
      else:
        print "Error finding node %s for way %s" % (nodeid, way.get('id'))
        
    out.write('<polyline points="%s" %s/>\n' % (points, style))
  
  out.write('</svg>')

#import cProfile
#cProfile.run('__main__()')
__main__()

