# -*- coding: utf-8 -*-
"""
HistoricalMap Plugin for Qgis
Made by Nicolas Karasiak and Antoine Lomellini
...
...

"""

import dataraster
import scipy as sp
from scipy import ndimage
import time

"""
  Filter class to isolate the forest and delete dark lines and fonts from historical map

  Input :
    inmImage : image to filter (text.jpg, text.tif...)
    outName : outname name of the filtered file (text)
    inShapeGrey : Size for the grey closing convolution matrix (odd number, int)
    inShapeMedian : Size for the median convolution matrix (odd  number, int)
    
  Output :
    New filtered file
    
"""
class historicalFilter:    
    def __init__(self, inImage,outName,inShapeGrey,inShapeMedian):
        # Try to load the image with dataraster.py (loadImage function)
        try:
            im,proj,geo,nl,nc,d=self.loadImage(inImage)
        except:
            print "Impossible to load the image"
        # Filter band per band using greyclosing and median filter
        try:
            filteredImage=self.filterBand(im,inShapeGrey,inShapeMedian,nl,nc,d)
        except:
            print "Impossible to filter"
        # Saving file
        try:
            self.writeImage(outName,filteredImage,geo,proj)
        except:
            print "Impossible to save the output image"
                
    def loadImage(self,inImage):
        """
        This function loads the image given its name.
        It makes a scipy array (im), give the projection, the geotransform and basics shape (nl,nc,d)
        
        Input : 
            inImage : map.tif...
        
        Output : 
            im : image as array (array)
            proj : the projection information
            geo : the geotransform information
            nl : number of lines (int)
            nc :  number of columns (int)
            d : number of dimension (int)
            
        """
        im,proj,geo=dataraster.open_data(inImage)
        nl,nc,d=im.shape
        return im,geo,proj,nl,nc,d
        
    def writeImage(self,outName,inImage,geo,proj):
        """
        Save the filtered array as an image
        
        Input :
            outName : Name of the output file
            inImage : Image to save
            geo : the geotransform information
            proj : the projection information
            
        Output :
            No return, but write image
        """
        dataraster.write_data(outName,inImage,geo,proj)
        
    def greyClose(self,inIm,out,inShapeGrey=11):
        """
        Perfom GreyClosing filter with square size as inShapeGrey, default is 11.
        """
        out[:,:]=ndimage.morphology.grey_closing(inIm[:,:],size=(inShapeGrey,inShapeGrey))
        return out.astype(inIm.dtype.name)
    
    def median(self,inIm,out,inShapeMedian=11):
        """
        Perfom median filter with square size as inShapeMedian, default is 11.
        """
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
    filtering=historicalFilter(folder+file,folder+'new_filtered.tif',11,11)
    t2=time.clock()
    print t2-t1,'seconds'

    

