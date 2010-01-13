from math import sin, cos, tan, atan, radians, pi, sqrt, atan2, asin
 
def vincenty(lat1,lon1, lat2, lon2):
    """returns distance in meters between any points earth"""
    
    a = 6378137
    b = 6356752.3142
    f = 1/298.257223563
    
    L = radians( lon2-lon1 )
    U1 = atan( (1-f) * tan( radians(lat1) ) )
    U2 = atan( (1-f) * tan( radians(lat2) ) )
    sinU1 = sin(U1); cosU1 = cos(U1)
    sinU2 = sin(U2); cosU2 = cos(U2)
    lmbda = L; lmbdaP = 2*pi
    
    iterLimit = 20
    
    while( iterLimit > 0 ):
        if abs(lmbda-lmbdaP) < 1E-12:
            break
        
        sinLambda = sin(lmbda); cosLambda = cos(lmbda)
        sinSigma = sqrt((cosU2*sinLambda) * (cosU2*sinLambda) + \
            (cosU1*sinU2-sinU1*cosU2*cosLambda) * (cosU1*sinU2-sinU1*cosU2*cosLambda))
        if sinSigma==0:
            return 0  # co-incident points
 
        cosSigma = sinU1*sinU2 + cosU1*cosU2*cosLambda
        sigma = atan2(sinSigma, cosSigma)
        alpha = asin(cosU1 * cosU2 * sinLambda / sinSigma)
        cosSqAlpha = cos(alpha) * cos(alpha)
        cos2SigmaM = cosSigma - 2*sinU1*sinU2/cosSqAlpha
        C = f/16*cosSqAlpha*(4+f*(4-3*cosSqAlpha))
        lmbdaP = lmbda;
        lmbda = L + (1-C) * f * sin(alpha) * \
            (sigma + C*sinSigma*(cos2SigmaM+C*cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)))
            
        iterLimit -= 1
            
    if iterLimit==0:
        return None  # formula failed to converge
 
    uSq = cosSqAlpha * (a*a - b*b) / (b*b);
    A = 1 + uSq/16384*(4096+uSq*(-768+uSq*(320-175*uSq)))
    B = uSq/1024 * (256+uSq*(-128+uSq*(74-47*uSq)))
    deltaSigma = B*sinSigma*(cos2SigmaM+B/4*(cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)-
            B/6*cos2SigmaM*(-3+4*sinSigma*sinSigma)*(-3+4*cos2SigmaM*cos2SigmaM)))
    s = b*A*(sigma-deltaSigma)
    
    return s