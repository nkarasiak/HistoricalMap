# -*- coding: utf-8 -*-
"""
HistoricalMap Plugin for Qgis
Made by Nicolas Karasiak and Antoine Lomellini
Teacher : Mathieu Fauvel, David Sheeren
Where ? ENSAT @ Toulouse
Github : https://github.com/lennepkade/Historical-Map/
"""

import time
import dataraster
import learn_model as lm
import classify_image as clf
from scipy import ndimage
import os


"""
  Filter class to isolate the forest, delete dark lines and fonts from Historical Map

  Input :
    inImage : image name to filter ('text.tif',str)
    outName : outname name of the filtered file (str)
    inShapeGrey : Size for the grey closing convolution matrix (odd number, int)
    inShapeMedian : Size for the median convolution matrix (odd  number, int)
    
  Output :
    -- Nothing except a raster file (outName)
    
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
            inImage : image name to filter ('text.tif',str)
            outName : outname name of the filtered file (str)
            inShapeGrey : Size for the grey closing convolution matrix (odd number, int)
            inShapeMedian : Size for the median convolution matrix (odd  number, int)
        
        Output :
            -- Nothing except a raster file (outName)
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
        
    
if __name__=='__main__':
    
    t1=time.clock()
#    
    # Image to work on

    inImage='data/map.tif'
        
    inFile,inExtension = os.path.splitext(inImage) # Split filename and extension
    outFilter=inFile+'_filtered'+inExtension 
    
    # Filtering....
    filtered=historicalFilter(inFile+inExtension,outFilter,inShapeGrey=11,inShapeMedian=11)
    print 'Image saved as : '+outFilter
    
    # Learn Model...
    outModel='data/ModelGMM'
    inVector='data/train.shp'
    model=lm.learn_model(inRaster=outFilter,inVector=inVector,inField='Class',inSplit=0.5,inSeed=0,outModel=outModel,inClassifier='GMM')   
    print 'Model saved as : '+outModel
    
    # Classify image...
    outRaster='data/outGMM.tif'
    outShpFolder='data/outSHP'
    classified=clf.classifyImage(inRaster=outFilter,inModel=outModel,outRaster=outRaster,outShpFolder=outShpFolder,inMinSize=8,inMask=None,inField='Class',inNODATA=-10000)
    
    
    print 'Classified image at : '+outRaster
    print 'Shp folder in : ' +outShpFolder
    print '3 Steps done in',time.clock()-t1,'seconds'
