from prender import processing
import csv
from slopespeed import cons
from numpy import polyfit

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
    
def get_median_line(data, left, right, bucketwidth=1, samplewidth=0.1, split=0.5):
    for i in floatrange(left,right,samplewidth):
        bucket = bucketize(i-bucketwidth,i+bucketwidth,data)
        bucket_median = median(bucket,split)
        if bucket_median:
            yield (i, bucket_median)
            
def eval_poly(coeffs, x):
    return sum([coeff*(x**(len(coeffs)-i-1)) for i, coeff in enumerate(coeffs)])
    
def draw_median_line(data, mr, left, right, bucketwidth=1, samplewidth=0.1, split=0.5):
    median_line = list( get_median_line( data, left, right, bucketwidth, samplewidth, split ) )

    for (x1,y1), (x2,y2) in cons(median_line,1):
        mr.line( x1,y1,x2,y2 )
    
def speed_on_slope(grade, speed, uphill_slowness, downhill_fastness):
    if grade < 0:
        raise ValueError( "can't handle downhill grades" )
        
    return (uphill_slowness*speed)/(uphill_slowness+grade)
            
def draw_fit_line(mr, left, right, coeffs):
    for x1, x2 in cons(list(floatrange(left,right,0.1)),1):
        mr.line( x1, eval_poly(coeffs, x1), x2, eval_poly(coeffs, x2) )
        
def plot(mr, left, right, func, res=0.1):
    for x1, x2 in cons(list(floatrange(left,right,res)),1):
        mr.line( x1, func(x1), x2, func(x2) )

def render_slopespeed_plot(data, map_out, phase_change_slope=4.5, uphill_slowness=0.05):
        
    xs = [x[0] for x in data]
    ys = [x[1] for x in data]
        
    left = min(xs)
    right = max(xs)
    bottom = 0#min(ys)
    top = max(ys)
    
    mr = processing.MapRenderer()
    mr.start(left,bottom,right,top,2000) #left,bottom,right,top,width
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
    for i in range(left, right, 1):
        mr.line(i, bottom, i, top)
    # grade-0 line
    mr.strokeWeight(0.01)
    mr.line(0,bottom,0,top)

    # speed lines
    mr.strokeWeight(0.001)
    mr.stroke(128,128,128,255)
    for y in range(top):
        mr.line(left,y,right,y)
        
    # graphserver lines
    mr.stroke(0,0,255)
    mr.strokeWeight(0.1)

    # draw downhill line
    downslope_coeffs = polyfit([x for x,y in data if x<=0],[y for x,y in data if x<=0],1)
    plot( mr, left, 0, lambda x: eval_poly(downslope_coeffs, x) )
    
    # draw phase change line
    B, C = downslope_coeffs
    y = speed_on_slope( phase_change_slope*0.01, C, uphill_slowness, 1.96 )
    A = (y - B*phase_change_slope-C)/(phase_change_slope**2)
    plot( mr, 0, phase_change_slope, lambda x: eval_poly([A,B,C], x) )
    
    print B, C, phase_change_slope
    
    # raw uphill line
    plot( mr, phase_change_slope, right, lambda x:speed_on_slope( x*0.01, C, uphill_slowness, 1.96 ) )
    
    # draw average lines            
    mr.stroke(255,0,0)
    mr.strokeWeight(0.01)
    draw_median_line( data, mr, left, right, split=0.1 )
    draw_median_line( data, mr, left, right, split=0.25 )
    draw_median_line( data, mr, left, right, split=0.75 )
    draw_median_line( data, mr, left, right, split=0.9 )

    mr.strokeWeight(0.03)
    draw_median_line( data, mr, left, right, split=0.5 )

    mr.saveLocal( map_out )
    mr.stop()
    
def main(csv_in, image_out):
    data = [(float(slope),float(speed)) for slope, speed in csv.reader( open( csv_in ) ) if float(speed)>0.80]
    render_slopespeed_plot( data, image_out )
    
if __name__=='__main__':
    main("out.csv", "map.png")