# -*- coding: utf-8 -*-
"""

"""

import dataraster
import scipy as sp
from scipy import ndimage
import time

"""
  Filter class to isolate the forest and delete dark lines and fonts.

  Input :
    inmin : image to filter
    inshape: shape of the convolution matrix used
    
  Output :
  
  METHODS :
    filtergreyclose()
    filtermedian()
    
"""
class historicalFilter:    
    def __init__(self, inImage,outName,inShapeGrey,inShapeMedian):
        """
        Initialize the historicalFilter class
        
        Given imagename, loads it, filter each band with greyfilter then medianfilter then save it as outname
        
        Input :
            inImage : 
            outName : 
            inShapeGrey : 
            inShapeMedian : 
        Output :
        """
        try:
            im,proj,geo,nl,nc,d=self.loadImage(inImage)
        except:
            print "Impossible to load the image"
        try:
            filteredImage=self.filterBand(im,inShapeGrey,inShapeMedian,nl,nc,d)
        except:
            print "Impossible to filter"
        try:
            self.writeImage(outName,filteredImage,geo,proj)
        except:
            print "Impossible to save the output image"
                
    def loadImage(self,inImage):
        """
        This function loads the image given its name.
        It makes a scipy array (im), give the projection, the geotransform and basics shape (nl,nc,d)
        
        Input : 
            inImage : tif...
        
        Output : 
            im : image as array
            proj : the projection information
            geo : the geotransform information
            nl : number of lines
            nc :  number of columns
            d : number of dimension
            
        """
        im,proj,geo=dataraster.open_data(inImage)
        nl,nc,d=im.shape
        return im,proj,geo,nl,nc,d
        
    def writeImage(self,outname,outimage,geo,proj):
        dataraster.write_data(outname,outimage,proj,geo)
        
    def greyClose(self,inIm,out,inShapeGrey=11):
        out[:,:]=ndimage.morphology.grey_closing(inIm[:,:],size=(inShapeGrey,inShapeGrey))
        return out.astype(inIm.dtype.name)
    
    def median(self,inIm,out,inShapeMedian=11):
        out[:,:]=ndimage.filters.median_filter(inIm[:,:],size=(inShapeMedian,inShapeMedian))
        return out.astype(inIm.dtype.name)
        
    def filterBand(self,inIm,inShapeGrey,inShapeMedian,nl,nc,d):
        """
        Filter band per band with greyClose and median
        Generate empty table then fill it with greyClose and median filter above it.
        
        Input :
            inIm : the loaded image (array)
            inShapeGrey : odd number (int)
            inShapeMedian : odd number (int)
            nl : number of lines of the table (int)
            nc : number of columns of the table (int)
            d : number of dimension (int)
            
        Output :
            out : filtered band (array)
        """
        try:
            out = sp.empty((nl,nc,d),dtype=inIm.dtype.name)
        except:
            print "Can't create empty table"    
        for i in range(d):
            greyF=self.greyClose(inIm[:,:,i],out[:,:,i],inShapeGrey)
            medianF=self.median(greyF,out[:,:,i],inShapeMedian)
            out[:,:,i]=medianF[:,:]
        return out                
        
if __name__=='__main__':
    # historicalFilter class
    folder="data/"
    file="map.tif"
    t1=time.clock()
    filtering=historicalFilter(folder+file,folder+file+'_filtered.tif',11,11)
    t2=time.clock()
    print t2-t1,'seconds'

    

