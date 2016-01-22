#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scipy as sp
#import argparse
import os
import pickle
from osgeo import gdal, ogr
import tempfile
import gmm_ridge as gmmr
from sklearn import neighbors
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import StratifiedKFold
from sklearn.grid_search import GridSearchCV

# Scale function
def scale(x,M=None,m=None):  # TODO:  DO IN PLACE SCALING
    ''' Function that standardize the data
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
def predict_image(raster_name,classif_name,model,mask_name=None,NODATA=-10000,SCALE=None):
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
            mask_temp=mask.GetRasterBand(1).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
            t = sp.where((mask_temp!=0) & (X[:,0]!=NODATA))[0]
            yp=sp.zeros((cols*lines,))

            # TODO: Change this part accorindgly ...
            if t.size > 0:
                yp[t]= model.predict(scale(X[t,:],M=M,m=m)).astype('uint8')
            
            # Write the data
            out.WriteArray(yp.reshape(lines,cols),j,i)
            out.FlushCache()
            del X,yp

    # Clean/Close variables    
    raster = None
    dst_ds = None

if __name__=='__main__':
    # Initiliaze parser
    
    inRaster='data/map.tif'
    inModel='data/ModelGMM'
    inMask='data/train.shp'
    inField='Class'
    out='data/outGMM.tif'
    inNODATA=-10000
    
#    parser = argparse.ArgumentParser(description="Classifiy an remote sensing image using fixed tree model")
#    parser.add_argument("-in_raster",help="Raster image to be classifier",type=str)
#    parser.add_argument("-in_model",help="Model",type=str)
#    parser.add_argument("-in_mask",help="Mask of selected pixel to be classified",type=str)
#    parser.add_argument("-out",help="Name of the output classified image",type=str)
#    parser.add_argument("-NODATA",help="NO DATA value",type=int, default=-10000)
#    args = parser.parse_args()

    # Build raster mask
    """ 
    rasterize with OTB 

    temp_folder = tempfile.mkdtemp()
    filename = os.path.join(temp_folder, 'temp.tif')
   
    OTB_application = 'otbcli_Rasterization -in '+inMask+' -out '+filename+' uint8 -im '+inRaster+' -mode attribute -mode.attribute.field '+inField    
    os.system(OTB_application)

    """
    
    """
    rasterize with Gdal
    """
    # Convert vector to raster
    temp_folder = tempfile.mkdtemp()
    filename = os.path.join(temp_folder, 'temp.tif')
    
    data = gdal.Open(inRaster,gdal.GA_ReadOnly)
    shp = ogr.Open(inMask)
    lyr = shp.GetLayer()

    # Create temporary data set
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(filename,data.RasterXSize,data.RasterYSize, 1,gdal.GDT_Byte)
    dst_ds.SetGeoTransform(data.GetGeoTransform())
    dst_ds.SetProjection(data.GetProjection())
    OPTIONS = 'ATTRIBUTE='+inField
    gdal.RasterizeLayer(dst_ds, [1], lyr, None,options=[OPTIONS])
    data,dst_ds,shp,lyr=None,None,None,None

    # Load model
    model = open(inModel,'rb') # TODO: Update to scale the data 
    if model is None:
        print "Model not load"
        exit()
    else:
        tree,M,m = pickle.load(model)
        
        model.close()

    # Process the data
    predict_image(inRaster,out,tree,mask_name=filename,NODATA=inNODATA,SCALE=[M,m])
    os.remove(filename)
    os.rmdir(temp_folder)
