# -*- coding: utf-8 -*-
"""
HistoricalMap Plugin for Qgis
Made by Nicolas Karasiak and Antoine Lomellini
Teacher : Mathieu Fauvel



"""

import dataraster
import scipy as sp
from scipy import ndimage
<<<<<<< HEAD
import time
=======
from osgeo import gdal
import time
import os
>>>>>>> beta

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
            data,im=self.loadImage(inImage)
        except:
            print "Impossible to load the image"
        # Filter band per band using greyclosing and median filter
        try:
            filteredImage=self.filterBand(data,im,outName,inShapeGrey,inShapeMedian)
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
            d : number of dimension (int)
            proj : the projection information
            geo : the geotransform information

        """
        data,im=dataraster.open_data_band(inImage)
        
        return data,im
        
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
        
#    def greyClose(self,inIm,out,inShapeGrey=11):
#        """
#        Perfom GreyClosing filter with square size as inShapeGrey, default is 11.
#        """
#        out[:,:]=ndimage.morphology.grey_closing(inIm[:,:],size=(inShapeGrey,inShapeGrey))
#        return out.astype(inIm.dtype.name)
#    
#    def median(self,inIm,out,inShapeMedian=11):
#        """
#        Perfom median filter with square size as inShapeMedian, default is 11.
#        """
#        out[:,:]=ndimage.filters.median_filter(inIm[:,:],size=(inShapeMedian,inShapeMedian))
#        return out.astype(inIm.dtype.name)
        
    def filterBand(self,data,im,outName,inShapeGrey,inShapeMedian):
        """
        Filter band per band with greyClose and median
        Generate empty table then fill it with greyClose and median filter above it.
        
        Input :
            inIm : the loaded image (array)
            inShapeGrey : odd number (int)
            inShapeMedian : odd number (int)
            d : number of dimension (int)
            
        Output :
            out : filtered image (array)
        """
#        try:
#            out = sp.empty((nl,nc,d),dtype=inIm.dtype.name)
#        except:
#            print "Can't create empty table"    
        
        # For each band (d), perform greyclosing then median filter
        # Save each band on the out table in the right dimension (i)
        
        proj = data.GetProjection()
        geo = data.GetGeoTransform()
        d = data.RasterCount
        print d
        outFile=dataraster.write_data_band(outName,im,d,geo,proj)
        print 'nombre de dimensions:'        
        print outFile.RasterCount
        for i in range(d):
            # Read data from the right band
            temp = data.GetRasterBand(i+1).ReadAsArray()
            # 
            temp = ndimage.morphology.grey_closing(temp,size=(inShapeGrey,inShapeGrey))
            temp = ndimage.filters.median_filter(temp,size=(inShapeMedian,inShapeMedian))
            # Write band
            final=outFile.GetRasterBand(i+1)
            final.WriteArray(temp)
            final.FlushCache()
            temp = None
            

        
if __name__=='__main__':
    # historicalFilter class
<<<<<<< HEAD
    folder="data/"
    t1=time.clock()
    filtering=historicalFilter(folder+'map.tif',folder+'filtered',11,11)
    t2=time.clock()
    resultat=t2-t1
    print resultat
=======
>>>>>>> beta

    folder="../projet/test/"
    file="map.tif"
    extension = os.path.splitext(folder+file)[1]
    
    filename, file_extension = os.path.splitext('../projet/test/map.tif')
    t1=time.clock()
    filtering=historicalFilter(folder+file,folder+'map_1111'+extension,11 ,11)
    t2=time.clock()
    print 'Filtering done in ',t2-t1,'seconds'
