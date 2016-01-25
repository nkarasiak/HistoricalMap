#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scipy as sp
#import argparse
#import os
import pickle
from osgeo import gdal, ogr
#import tempfile
#import gmm_ridge as gmmr
#from sklearn import neighbors
#from sklearn.svm import SVC
#from sklearn.ensemble import RandomForestClassifier
#from sklearn.cross_validation import StratifiedKFold
#from sklearn.grid_search import GridSearchCV

# Scale function

"""
  Classify image with learn clasifier and learned model

  Input :
    inRaster : Filtered image name ('sample_filtered.tif',str)
    inModel : outname name of the filtered file ('training.shp',str)
    outRaster : Raster name to save ('classifiedimage.tif', str)
    outShpFolder : Folder where will be stored shp files ('shps',str)
    inMinSize : min size in acre for the forest, ex 6 means all polygons below 6000 m2 (int)
    TODO inMask : Mask size where no classification is done                                     |||| NOT YET IMPLEMENTED
    inField : Column name where are stored class number (str)
    inNODATA : if NODATA (int)
        
  Output :
    Raster image and the simple classification
    SHP file with deleted polygon below inMinSize
    
"""

class classifyImage:
    def __init__(self,inRaster,inModel,outRaster,outShpFolder='data/outSHP',inMinSize=6000,inMask=None,inField='Class',inNODATA=-10000):
            # Load model
        model = open(inModel,'rb') # TODO: Update to scale the data 
        if model is None:
            print "Model not load"
            exit()
        else:
            tree,M,m = pickle.load(model)
            
            model.close()
    
        # Process the data
        self.predict_image(inRaster,outRaster,tree,None,NODATA=inNODATA,SCALE=[M,m])
       
        
        # Vectorize with field inField
        
        
        sourceRaster = gdal.Open(outRaster)
        band = sourceRaster.GetRasterBand(1)
        bandArray = band.ReadAsArray()
        outShapefile = outShpFolder
        driver = ogr.GetDriverByName("ESRI Shapefile")
        driver.DeleteDataSource(outShpFolder)
        outDatasource = driver.CreateDataSource(outShpFolder)
        outLayer = outDatasource.CreateLayer("polygonized", srs=None)
        newField = ogr.FieldDefn(inField, ogr.OFTInteger)
        outLayer.CreateField(newField)
            
        gdal.Polygonize(band, None,outLayer, 0,[],callback=None)  
        outDatasource.Destroy()
        sourceRaster = None
        
        # Add area
        ds = ogr.Open(outShpFolder, update = 1 )
        
        lyr = ds.GetLayerByIndex(0)
        lyr.ResetReading()
        
        field_defn = ogr.FieldDefn( "Area", ogr.OFTReal )
        lyr.CreateField(field_defn)
        
        for i in lyr:
            # feat = lyr.GetFeature(i) 
            geom = i.GetGeometryRef()
            area = round(geom.GetArea()/1000,0)
            lyr.SetFeature(i)
            i.SetField( "Area", area )
            lyr.SetFeature(i)
            if area<6:
                lyr.DeleteFeature(i.GetFID())
        ds = None
        
    def scale(self,x,M=None,m=None):  # TODO:  DO IN PLACE SCALING
        ''' Function that standardize the datouta
            Input:
                x: the data
                M: the Max vector
                m: the Min vector
            Output:
                x: the standardize data
                M: the Max vector
                m: the Min vector
        '''
        [n,d]=x.shape
        if not sp.issubdtype(x.dtype,float):
            x=x.astype('float')
    
        # Initialization of the output
        xs = sp.empty_like(x)
    
        # get the parameters of the scaling
        if M is None:
            M,m = sp.amax(x,axis=0),sp.amin(x,axis=0)
            
        den = M-m
        for i in range(d):
            if den[i] != 0:
                xs[:,i] = 2*(x[:,i]-m[i])/den[i]-1
            else:
                xs[:,i]=x[:,i]
    
        return xs
    def predict_image(self,raster_name,classif_name,model,mask_name=None,NODATA=-10000,SCALE=None):
        '''
            The function classify the whole raster image, using per block image analysis. The classifier is given in classifier and options in kwargs
        '''
        # Open Raster and get additionnal information
        raster = gdal.Open(raster_name,gdal.GA_ReadOnly)
        if raster is None:
            print 'Impossible to open '+raster_name
            exit()
        
        # If provided, open mask
        if mask_name is None:
            mask=None
        else:
            mask = gdal.Open(mask_name,gdal.GA_ReadOnly)
            if mask is None:
                print 'Impossible to open '+mask_name
                exit()
            # Check size
            if (raster.RasterXSize != mask.RasterXSize) or (raster.RasterYSize != mask.RasterYSize):
                print 'Image and mask should be of the same size'
                exit()   
        if SCALE is not None:
            M,m=sp.asarray(SCALE[0]),sp.asarray(SCALE[1])
            
        # Get the size of the image
        d  = raster.RasterCount
        nc = raster.RasterXSize
        nl = raster.RasterYSize
        
        # Get the geoinformation    
        GeoTransform = raster.GetGeoTransform()
        Projection = raster.GetProjection()
        
        # Get block size
        band = raster.GetRasterBand(1)
        block_sizes = band.GetBlockSize()
        x_block_size = block_sizes[0]
        y_block_size = block_sizes[1]
        del band
        
        ## Initialize the output
        driver = gdal.GetDriverByName('GTiff')
        dst_ds = driver.Create(classif_name, nc,nl, 1, gdal.GDT_Byte)
        dst_ds.SetGeoTransform(GeoTransform)
        dst_ds.SetProjection(Projection)
        out = dst_ds.GetRasterBand(1)
        
        ## Perform the classification
        for i in range(0,nl,y_block_size):
            if i + y_block_size < nl: # Check for size consistency in Y
                lines = y_block_size
            else:
                lines = nl - i
            for j in range(0,nc,x_block_size): # Check for size consistency in X
                if j + x_block_size < nc:
                    cols = x_block_size
                else:
                    cols = nc - j
                           
                # Load the data and Do the prediction
                X = sp.empty((cols*lines,d))
                for ind in xrange(d):
                    X[:,ind] = raster.GetRasterBand(int(ind+1)).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
                    
                # Do the prediction
                if mask is None:
                    mask_temp=raster.GetRasterBand(1).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
                    t = sp.where((mask_temp!=0) & (X[:,0]!=NODATA))[0]
                    yp=sp.zeros((cols*lines,))
                else :
                    mask_temp=mask.GetRasterBand(1).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
                    t = sp.where((mask_temp!=0) & (X[:,0]!=NODATA))[0]
                    yp=sp.zeros((cols*lines,))
    
                # TODO: Change this part accorindgly ...
                if t.size > 0:
                    yp[t]= model.predict(self.scale(X[t,:],M=M,m=m)).astype('uint8')
                
                # Write the data
                out.WriteArray(yp.reshape(lines,cols),j,i)
                out.FlushCache()
                del X,yp
    
        # Clean/Close variables    
        raster = None
        dst_ds = None


if __name__=='__main__':
    classified=classifyImage(inRaster='data/map_filtered.tif',inModel='data/ModelGMM',outRaster='data/outGMM.tif',outShpFolder='data/outSHP',inMinSize=6000,inMask=None,inField='Class',inNODATA=-10000)


