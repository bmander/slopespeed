from xml.dom.minidom import parse, parseString
from datetime import datetime
from vincenty import vincenty
from gridfloat import GridFloat

def cons(ary,width=2):
  """return each two consecutive elements"""
  for i in range(len(ary)-width):
    yield ary[i], ary[i+width]

def parse_trackpoint( trkpt ):
  """parse GPX trkpt tag into a (float,float,datetime) tuple"""
  lat = float( trkpt.getAttribute( "lat" ) )
  lon = float( trkpt.getAttribute( "lon" ) )
  time = datetime.strptime( trkpt.getElementsByTagName("time")[0].firstChild.data, "%Y-%m-%dT%H:%M:%SZ")
  return (lat, lon, time)
  
def parse_trackseg( trkseg ):
  """parse GPX trkseg tag into a list of (float,float,datetime) tuples"""
  for trkpt in trkseg.getElementsByTagName( "trkpt" ):
    yield parse_trackpoint( trkpt )

def get_tracksegs( gpx_filename ):
  """get a list of parsed tracksegs given a GPX filename"""
  dom1 = parse( gpx_filename )

  for trkseg in dom1.getElementsByTagName( "trkseg" ):
    yield list(parse_trackseg( trkseg ))

def main(fileins, fileout):
  out = open( fileout, "w" )

  gf = GridFloat( "./data/34293486/34293486" )

  for filein in fileins:
    print "working on %s"%filein
    for track in get_tracksegs( filein ):
      for (lat1, lon1, time1), (lat2, lon2, time2) in cons(track, 3):
        e1 = gf.elevation( lon1, lat1 )
        e2 = gf.elevation( lon2, lat2 )
  
        dx = vincenty(lat1, lon1, lat2, lon2)
        dy = e2-e1
        dt = (time2-time1).seconds
  
        if dt==0:
          print "teleported %f"%dt
          continue
        if dx==0:
	        continue
    
        v = dx/dt
        grade = (dy/dx)*100

        out.write( "%s,%s\n"%(grade,v) )

if __name__=='__main__':
    print "starting"
    #main( ("./data/royaltek.gpx", "./data/BallardTrip.gpx", "./data/Track4.gpx", "./data/Track5.gpx", "./data/Track6.gpx", "./data/Track7.gpx", "./data/Track8.gpx", "./data/Track9.gpx",), "out.csv" )
    main( ("data.gpx",), "out2.csv" )
    print "done"