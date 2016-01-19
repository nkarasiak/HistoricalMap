# -*- coding: utf-8 -*-
"""

"""

import dataraster
import scipy as sp
import scipy.ndimage



"""
  Filter class to isolate the forest and delete dark lines/fonts above.


  ATTRIBUTES :
    inmin : image to filter
    inshape: shape of the convolution matrix used
    
  METHODS :
    filtergreyclose()
    filtermedian()

"""
class historicalFilter:    
    def __init__(self, inimage,outname,inShapeGrey,inShapeMedian):
        im,proj,geo=self.loadImage(inimage)
        greyf=self.greyClose(im,inShapeGrey)
        medianf=self.median(greyf,inShapeMedian)
        self.writeImage(outname,medianf,geo,proj)
                
    def loadImage(self,inimage):
        im,proj,geo=dataraster.open_data(inimage)
        return im,proj,geo
        
    def writeImage(self,outname,ioimage,geo,proj):
        dataraster.write_data(outname,ioimage,proj,geo)
        
    def greyClose(self,inim,inshape=11):
        [nl,nc,d]=inim.shape
        out = sp.empty((nl,nc,d),dtype=inim.dtype.name)
        for i in range(d):
            out[:,:,i]=sp.ndimage.morphology.grey_closing(inim[:,:,i],size=(inshape,inshape))
        return out.astype(inim.dtype.name)
    
    def median(self,inim,inshape=11):
        [nl,nc,d]=inim.shape
        out = sp.empty((nl,nc,d),dtype=inim.dtype.name)
        for i in range(d):
            out[:,:,i]=sp.ndimage.filters.median_filter(inim[:,:,i],size=(inshape,inshape))
        return out.astype(inim.dtype.name)
       

if __name__=='__main__':
    # Create an instance of historicalFilter class
    filtering=historicalFilter('map.tif','filtered',11,11)
    

