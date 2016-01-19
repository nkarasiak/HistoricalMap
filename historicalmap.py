# -*- coding: utf-8 -*-
"""

"""

import dataraster
import scipy as sp
import scipy.ndimage

im,proj,geo=dataraster.open_data('map.tif')
[nl,nc,d]=im.shape
out = sp.empty((nl,nc,d),dtype=im.dtype.name)




"""
  Filter class to isolate the forest and delete lines and names.


  ATTRIBUTES :
    inmin : image to filter
    inshape: shape of the convolution matrix used
    
  METHODS :
    filtergreyclose()
    filtermedian()

"""
class historicalFilter:    
    
    def loadImage(self,inimage):
        im,proj,geo=dataraster.open_data(inimage)
        [nl,nc,d]=im.shape
        out = sp.empty((nl,nc,d),dtype=im.dtype.name)
        return im,proj,geo,out
    def writeImage(self,outname,ioimage,geo,proj):
        dataraster.write_data(outname,ioimage,proj,geo)
    def greyClose(self,inim,inshape=11):
        for i in range(d):
            out[:,:,i]=sp.ndimage.morphology.grey_closing(inim[:,:,i],size=(inshape,inshape))
        return out.astype(im.dtype.name)
    
    def median(self,inim,inshape=11):
        for i in range(d):
            out[:,:,i]=sp.ndimage.filters.median_filter(inim[:,:,i],size=(inshape,inshape))
        return out.astype(im.dtype.name)


if __name__=='__main__':
    # Create an instance of historicalFilter class
    filtering=historicalFilter()
    
    # Load map
    im,proj,geo,imout=filtering.loadImage('map.tif')
    # Applying grey filter then median filter)
    greyf=filtering.greyClose(im,11)
    print 'greyf is done'
    medianf=filtering.median(greyf,11)
    print 'medianf is done'
    
    # Save filtered image
    filtering.writeImage('namefiltered',medianf,geo,proj)
    
