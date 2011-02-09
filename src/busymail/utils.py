import os, fnmatch, time, math

def seconds2days(s):
    return s / (24 * 60 * 60)


def datetime2timestamp(d, other=None):
    return time.mktime(d.timetuple())
        
def percentile(x, percent, key=lambda x:x):
    # from http://code.activestate.com/recipes/511478-finding-the-percentile-of-the-values/
    import math
    N = sorted(x.flat)
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (k-f)
    d1 = key(N[int(c)]) * (c-k)
    return d0+d1
    
def find_files(directory, pattern):    
    for root, dirs, files in os.walk(directory):       
        for basename in files:            
            if fnmatch.fnmatch(basename, pattern):                
                filename = os.path.join(root, basename)                
                yield filename
