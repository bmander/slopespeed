from math import floor
import struct

class GridFloat:
    def __init__(self, basename):
        try:
          self._read_header( basename + ".hdr" )
        except IOError:
          raise IOError( "no such file '%s.hdr'"%basename)
        self.fp = open( basename + ".flt", "rb" )
        
    def _read_header(self, filename):
        fp = open( filename, "r" )
        
        self.ncols      = int( fp.readline()[14:].strip() )
        self.nrows      = int( fp.readline()[14:].strip() )
        self.xllcorner  = float( fp.readline()[14:].strip() )
        self.yllcorner  = float( fp.readline()[14:].strip() )
        self.cellsize   = float( fp.readline()[14:].strip() )
        self.NODATA_value = int( fp.readline()[14:].strip() )
        self.byteorder  = "<" if fp.readline()[14:].strip()=="LSBFIRST" else ">"
        
        self.left = self.xllcorner
        self.right = self.xllcorner + (self.ncols-1)*self.cellsize
        self.bottom = self.yllcorner
        self.top = self.yllcorner + (self.nrows-1)*self.cellsize
    
    @property
    def extent(self):
        return ( self.xllcorner, 
                 self.yllcorner, 
                 self.xllcorner+self.cellsize*(self.ncols-1), 
                 self.yllcorner+self.cellsize*(self.nrows-1) )
                 
    def contains(self, lng, lat):
        return not( lng < self.left or lng >= self.right or lat <= self.bottom or lat > self.top )
    
    def allcells(self):
        self.fp.seek(0)
        return struct.unpack( "%s%df"%(self.byteorder, self.nrows*self.ncols), self.fp.read())
        
    def extremes(self):
        mem = self.allcells()
        return (min(mem), max(mem))
    
    def cell( self, x, y ):
        position = (y*self.ncols+x)*4
        self.fp.seek(position)
        return struct.unpack( "%sf"%(self.byteorder), self.fp.read( 4 ) )[0]
        
    def elevation( self, lng, lat, interpolate=True ):
        if lng < self.left or lng >= self.right or lat <= self.bottom or lat > self.top:
            return None
        
        x = (lng-self.left)/self.cellsize
        y = (self.top-lat)/self.cellsize
        
        ulx = int(floor(x))
        uly = int(floor(y))
        
        ul = self.cell( ulx, uly )
        if not interpolate:
            return ul
        ur = self.cell( ulx+1, uly ) 
        ll = self.cell( ulx, uly+1 )
        lr = self.cell( ulx+1, uly+1 )
        
        cellleft = x%1
        celltop = y%1
        um = (ur-ul)*cellleft+ul #uppermiddle
        lm = (lr-ll)*cellleft+ll #lowermiddle
        
        return (lm-um)*celltop+um
        
    def profile(self, points, resolution=10):
        return [(s, self.elevation( lng, lat )) for lng, lat, s in split_line_string(points, resolution)]