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
    New filtered file
    
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
        data,im=dataraster.open_data_band(inImage)

        # get proj,geo and dimension (d) from data
        proj = data.GetProjection()
        geo = data.GetGeoTransform()
        d = data.RasterCount

        # create empty geotiff with d dimension, geotransform & projection
        outFile=dataraster.write_data_band(outName,im,d,geo,proj)
        
        # fill outFile with filtered band
        for i in range(d):
            # Read data from the right band
            temp = data.GetRasterBand(i+1).ReadAsArray()
            # Filter with greyclosing, then with median filter
            temp = ndimage.morphology.grey_closing(temp,size=(inShapeGrey,inShapeGrey))
            temp = ndimage.filters.median_filter(temp,size=(inShapeMedian,inShapeMedian))
            # Save bandand outFile
            out=outFile.GetRasterBand(i+1)
            out.WriteArray(temp)
            out.FlushCache()
            temp = None
            

if __name__=='__main__':
    # historicalFilter class


    folder="../projet/test/"
    file="map.tif"
    extension = os.path.splitext(folder+file)[1]
    
    filename, file_extension = os.path.splitext('../projet/test/map.tif')
    t1=time.clock()
    filtering=historicalFilter(folder+file,folder+'map_1111'+extension,11 ,11)
    t2=time.clock()
    print 'Filtering done in ',t2-t1,'seconds'
