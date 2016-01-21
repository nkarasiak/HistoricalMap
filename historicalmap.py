# -*- coding: utf-8 -*-
"""
HistoricalMap Plugin for Qgis
Made by Nicolas Karasiak and Antoine Lomellini
Teacher : Mathieu Fauvel



"""
from osgeo import gdal
import time
import dataraster
import scipy as sp
from scipy import ndimage
import os

"""
  Filter class to isolate the forest and delete dark lines and fonts from historical map

  Input :
    inmImage : image to filter (text.jpg, text.tif...)
    outName : outname name of the filtered file (text)
    inShapeGrey : Size for the grey closing convolution matrix (odd number, int)
    inShapeMedian : Size for the median convolution matrix (odd  number, int)
    
  Output :
    Nothing, except a geoTiff file
    
"""

class historicalFilter:    
    def __init__(self, inImage,outName,inShapeGrey,inShapeMedian):
        # Try to load the image with dataraster.py (loadImage function)
        try:
            self.filterBand(inImage,outName,inShapeGrey,inShapeMedian)
        except:
            print "Impossible to filter"
        # Saving file
       
    def filterBand(self,inImage,outName,inShapeGrey,inShapeMedian):
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
        # open data with Gdal
        try:
            data,im=dataraster.open_data_band(inImage)
        except:
            print 'Cannot load image'

        # get projection,geotransformation and dimension (d) from data
        proj = data.GetProjection()
        geo = data.GetGeoTransform()
        d = data.RasterCount

        # create empty geotiff with d dimension, geotransform & projection
        try:
            outFile=dataraster.write_data_band(outName,im,d,geo,proj)
        except:
            print 'Cannot write empty file'
        
        # fill outFile with filtered band
        for i in range(d):
            # Read data from the right band
            temp = data.GetRasterBand(i+1).ReadAsArray()
            # Filter band with greyclosing, then with median filter
            try:
                temp = ndimage.morphology.grey_closing(temp,size=(inShapeGrey,inShapeGrey))
            except: 
                print 'Cannot filter with Grey-Closing'
            try:
                temp = ndimage.filters.median_filter(temp,size=(inShapeMedian,inShapeMedian))
            except: 
                print 'Cannot filter with Median filter'
                
            # Save band in outFile
            try:
                out=outFile.GetRasterBand(i+1)
                out.WriteArray(temp)
                out.FlushCache()
                temp = None
            except:
                print 'Cannot save filtered band'
            

if __name__=='__main__':

    # get inImage (C:/img/test), and inExt (.tif)
    inImage,inExt= os.path.splitext('../projet/test/map.tif')
    t1=time.clock()
    
    filtering=historicalFilter(inImage+inExt,inImage+'_filtered'+inExt,11 ,11)
    t2=time.clock()
    print 'Filtering done in ',t2-t1,'seconds'
