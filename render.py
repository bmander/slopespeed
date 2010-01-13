from prender import processing
import csv
from slopespeed import cons

def floatrange(low, high, step):
    cursor=low
    while cursor<=high:
        yield cursor
        cursor+=step

def bucketize(low, high, data):
    return [speed for slope,speed in data if slope >= low and slope <= high]
        
def mean(ary):
    return sum(ary)/float(len(ary))
    
def median(ary,split=0.5):
    if len(ary)==0:
        return None
        
    ret = list(sorted(ary))[int(len(ary)*split)]
    return ret

data = [(float(slope),float(speed)) for slope, speed in csv.reader( open( "out.csv" ) ) if float(speed)>0.80]

mr = processing.MapRenderer()
mr.start(-20,0,20,12,2000) #left,bottom,right,top,width
mr.smooth()
mr.background(255,255,255)
mr.fill(0,0,0,20)
mr.stroke(0,0,0,0)
mr.strokeWeight(0)

for slope, speed in data:
    mr.ellipse( slope, speed, 0.12, 0.12 )

# grade lines
mr.strokeWeight(0.001)
mr.stroke(128,128,128,255)
for i in range(20):
    mr.line(i, 0, i, 12)
    mr.line(-i, 0, -i, 12)
# grade-0 line
mr.strokeWeight(0.01)
mr.line(0,0,0,12)

# speed lines
mr.strokeWeight(0.001)
mr.stroke(128,128,128,255)
for y in range(12):
    mr.line(-20,y,20,y)

# draw average lines
def draw_median_line(mr, bucketwidth=1, samplewidth=0.1, split=0.5):
    mean_line = []
    for i in floatrange(-20,20,samplewidth):
        bucket = bucketize(i-bucketwidth,i+bucketwidth,data)
        bucket_median = median(bucket,split)
        if bucket_median:
            mean_line.append( (i, bucket_median) )

    for (x1,y1), (x2,y2) in cons(mean_line,1):
        mr.line( x1,y1,x2,y2 )
        
mr.stroke(255,0,0)
mr.strokeWeight(0.01)
draw_median_line( mr, split=0.1 )
draw_median_line( mr, split=0.25 )
draw_median_line( mr, split=0.75 )
draw_median_line( mr, split=0.9 )

mr.strokeWeight(0.03)
draw_median_line( mr, split=0.5 )

mr.saveLocal("map.png")
mr.stop()