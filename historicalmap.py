# -*- coding: utf-8 -*-
"""
HistoricalMap Plugin for Qgis
Made by Nicolas Karasiak and Antoine Lomellini
Teacher : Mathieu Fauvel, David Sheeren & Claude Monteil



"""
from osgeo import gdal
import time
import dataraster
import scipy as sp
import learn_model as lm
import classify_image as clf
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
        try:
            data,im=dataraster.open_data_band(inImage)
        except:
            print 'Cannot open image'

        # get proj,geo and dimension (d) from data
        proj = data.GetProjection()
        geo = data.GetGeoTransform()
        d = data.RasterCount

        # create empty geotiff with d dimension, geotransform & projection
        try:
            outFile=dataraster.write_data_band(outName,im,d,geo,proj)
        except:
            print 'Cannot write empty image '+outName
        
        # fill outFile with filtered band
        for i in range(d):
            # Read data from the right band
            try:
                temp = data.GetRasterBand(i+1).ReadAsArray()
            except:
                print 'Cannot get rasterband'+i
            # Filter with greyclosing, then with median filter
            try:
                temp = ndimage.morphology.grey_closing(temp,size=(inShapeGrey,inShapeGrey))
            except:
                print 'Cannot filter with Grey_Closing'
            try:
                temp = ndimage.filters.median_filter(temp,size=(inShapeMedian,inShapeMedian))
            except:
                print 'Cannot filter with Median'
                
            # Save bandand outFile
            try:
                out=outFile.GetRasterBand(i+1)
                out.WriteArray(temp)
                out.FlushCache()
                temp = None
            except:
                print 'Cannot save band '+i+' on image '+outName
        

"""
class learnParcel(inRaster,inVector,inField,inClassifier,inModel,inSplit,inSeed):
    def __init__(self):
    print 'nothing'        

    def learn(inRaster,inVector,inField,inClassifier,inModel,inSplit,inSeed):
    learn_model.train('data/minGeoDec1.tif','data/ROI_m.shp','type')
    
"""    
    
if __name__=='__main__':
    # get inFile (data/map) and inExtension (.tif)
    #inFile,inExtension = os.path.splitext('data/map_rpj.tif')
    t1=time.clock()

#    inFile,inExtension = os.path.splitext('data/map.tif')
#    print 'Filtering done in ',time.clock()-t1,'seconds'
#    filteredImage=inFile+'_filtered'+inExtension
#    filtering=historicalFilter(inFile+inExtension,filteredImage,11,11)
    
    #    lm.train('data/map_filtered.tif','data/train.shp','Class',0.5,0,'data/ModelRF','RF')   
    lm.train('data/100mo/minGeoDec1_filtered.tif','data/100mo/ROI_m.shp','Class',0.5,0,'data/100mo/ModelGMM','GMM')   
    #clf.inRaster,inModel,inMask,inOut,NODATA
    print 'Learning done in',time.clock()-t1,'seconds'
    
    
    
    t2=time.clock()
    
