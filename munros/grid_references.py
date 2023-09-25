
from math import atan2, floor, pi, sqrt

#ref1 and 2 are fully numeric references without the prefix.
def grid_distance(ref1, ref2):
    deltaE = int(ref2.e)-int(ref1.e)
    deltaN = int(ref2.n)-int(ref1.n)
    
    dist_meters = sqrt(deltaE*deltaE + deltaN*deltaN)
    
    return round(dist_meters)
    