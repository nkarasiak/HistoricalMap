# -*- coding: utf-8 -*-
"""

"""

import dataraster
import scipy as sp
import scipy.ndimage

"""

"""
im,proj,geo=dataraster.open_data('map.tif')
[nl,nc,d]=im.shape
out = sp.empty((nl,nc,d),dtype=im.dtype.name)




"""
Filter class to isolate the forest and delete lines and names.
ATTRIBUTES :
inmin
inshape:
METHODS :
filtergreyclose
filtermedian

"""


def maxfilter(inim,inshape=11):
    for i in range(d):
        out[:,:,i]=sp.ndimage.filters.maximum_filter(inim[:,:,i],size=(inshape,inshape))
    return out.astype(im.dtype.name)                       
    
def minfilter(inim,inshape=3):
    for i in range(d):
        out[:,:,i]=sp.ndimage.filters.minimum_filter(inim[:,:,i],size=(inshape,inshape))
    return out.astype(im.dtype.name)
    
def greyclose(inim,inshape=11):
    for i in range(d):
        out[:,:,i]=sp.ndimage.morphology.grey_closing(inim[:,:,i],size=(inshape,inshape))
    return out.astype(im.dtype.name)

def median(inim,inshape=11):
    for i in range(d):
        out[:,:,i]=sp.ndimage.filters.median_filter(inim[:,:,i],size=(inshape,inshape))
    return out.astype(im.dtype.name)
    

#greyclose=greyclose(im)

#medianfilter=median(im)
#minfilter=minfilter(medianfilter)
maxfilter=maxfilter(im)
minfilter=minfilter(maxfilter)
medianfilter=median(minfilter)
#greyfilter=greyclose(medianfilter)
#dataraster.write_data('grey',greyclose,proj,geo)
dataraster.write_data('min',medianfilter,proj,geo)
#median=filtermedian(greyclose)


# grey=sp.ndimage.morphology.grey_closing(levelone)
