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
import pickle
import os
import accuracy_index as ai
import tempfile
import gmm_ridge as gmmr
import scipy as sp
from scipy import ndimage
from osgeo import gdal, ogr
from sklearn import neighbors
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import StratifiedKFold
from sklearn.grid_search import GridSearchCV

class historicalFilter:  
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
                
class learn_model:
    """
    Learn model with a shp file and a raster image
    
    Input :
        inRaster : Filtered image name ('sample_filtered.tif',str)
        inVector : Name of the training shpapefile ('training.shp',str)
        inField : Column name where are stored class number (str)
        inSplit : (int)
        inSeed : (int)
        outModel : Name of the model to save, will be compulsory for the 3rd step (classifying)
        inClassifier : GMM,KNN,SVM, or RF. (str)
        
    Output :
        Model file
        Confusion Matrix
        
    """
    def __init__(self,inRaster,inVector,inField='Class',inSplit=0.5,inSeed=0,outModel=None,inClassifier='GMM'):
           
        # Convert vector to raster
        temp_folder = tempfile.mkdtemp()
        filename = os.path.join(temp_folder, 'temp.tif')
        
        data = gdal.Open(inRaster,gdal.GA_ReadOnly)
        shp = ogr.Open(inVector)
        lyr = shp.GetLayer()
    
        # Create temporary data set
        driver = gdal.GetDriverByName('GTiff')
        dst_ds = driver.Create(filename,data.RasterXSize,data.RasterYSize, 1,gdal.GDT_Byte)
        dst_ds.SetGeoTransform(data.GetGeoTransform())
        dst_ds.SetProjection(data.GetProjection())
        OPTIONS = 'ATTRIBUTE='+inField
        gdal.RasterizeLayer(dst_ds, [1], lyr, None,options=[OPTIONS])
        data,dst_ds,shp,lyr=None,None,None,None
    
        
        # Load Training set
        X,Y =  dataraster.get_samples_from_roi(inRaster,filename)
        
        [n,d] = X.shape
        C = int(Y.max())
        SPLIT = inSplit
        os.remove(filename)
        os.rmdir(temp_folder)
        
        # Scale the data
        X,M,m = self.scale(X)
    
        # Learning process take split of groundthruth pixels for training and the remaining for testing
        if SPLIT < 1:
            # Random selection of the sample
            x = sp.array([]).reshape(0,d)
            y = sp.array([]).reshape(0,1)
            xt = sp.array([]).reshape(0,d)
            yt = sp.array([]).reshape(0,1)
            
            sp.random.seed(inSeed) # Set the random generator state
            for i in range(C):            
                t = sp.where((i+1)==Y)[0]
                nc = t.size
                ns = int(nc*SPLIT)
                rp =  sp.random.permutation(nc)
                x = sp.concatenate((X[t[rp[0:ns]],:],x))
                xt = sp.concatenate((X[t[rp[ns:]],:],xt))
                y = sp.concatenate((Y[t[rp[0:ns]]],y))
                yt = sp.concatenate((Y[t[rp[ns:]]],yt))
        else:
            x,y=X,Y
    
        # Train Classifier
        if inClassifier == 'GMM':
            # tau=10.0**sp.arange(-8,8,0.5)
            model = gmmr.GMMR()
            model.learn(x,y)
            # htau,err = model.cross_validation(x,y,tau)
            # model.tau = htau
        elif inClassifier == 'RF':
            param_grid_rf = dict(n_estimators=5**sp.arange(1,5),max_features=sp.arange(1,int(sp.sqrt(d))+10,2))
            y.shape=(y.size,)    
            cv = StratifiedKFold(y, n_folds=5)
            grid = GridSearchCV(RandomForestClassifier(), param_grid=param_grid_rf, cv=cv,n_jobs=-1)
            grid.fit(x, y)
            model = grid.best_estimator_
            model.fit(x,y)        
        elif inClassifier == 'SVM':
            param_grid_svm = dict(gamma=2.0**sp.arange(-4,4), C=10.0**sp.arange(-2,5))
            y.shape=(y.size,)    
            cv = StratifiedKFold(y, n_folds=5)
            grid = GridSearchCV(SVC(), param_grid=param_grid_svm, cv=cv,n_jobs=-1)
            grid.fit(x, y)
            model = grid.best_estimator_
            model.fit(x,y)
        elif inClassifier == 'KNN':
            param_grid_knn = dict(n_neighbors = sp.arange(1,50,5))
            y.shape=(y.size,)    
            cv = StratifiedKFold(y, n_folds=5)
            grid = GridSearchCV(neighbors.KNeighborsClassifier(), param_grid=param_grid_knn, cv=cv,n_jobs=-1)
            grid.fit(x, y)
            model = grid.best_estimator_
            model.fit(x,y)
    
        # Assess the quality of the model
        if SPLIT < 1 :
            # if  inClassifier == 'GMM':
            #     yp = model.predict(xt)[0]
            # else:
            yp = model.predict(xt)
            CONF = ai.CONFUSION_MATRIX()
            CONF.compute_confusion_matrix(yp,yt)
            sp.savetxt(str(inClassifier)+'_'+str(inSeed)+'_confu.csv',CONF.confusion_matrix,delimiter=',',fmt='%1.4d')
            
    
        # Save Tree model
        if outModel is not None:
            output = open(outModel, 'wb')
            pickle.dump([model,M,m], output)
            output.close()
    def scale(self,x,M=None,m=None):
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
        M,m = sp.amax(x,axis=0),sp.amin(x,axis=0)
        den = M-m
        for i in range(d):
            if den[i] != 0:
                xs[:,i] = 2*(x[:,i]-m[i])/den[i]-1
            else:
                xs[:,i]=x[:,i]
    
        return xs,M,m
        
class classifyImage():
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
    def __init__(self,inRaster,inModel,outRaster,outShpFolder='data/outSHP/',inMinSize=6,inMask=None,inField='Class',inNODATA=-10000):
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
        outLayer = outDatasource.CreateLayer("vectorized", srs=None)
        newField = ogr.FieldDefn(inField, ogr.OFTInteger)
        outLayer.CreateField(newField)
            
        gdal.Polygonize(band, None,outLayer, 0,[],callback=None)  
        outDatasource.Destroy()
        sourceRaster = None
        
        # Add area for each feature
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
        # 
            if area<inMinSize: #Size in acre (/1000) for the 2154 projection
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
    model=learn_model(inRaster=outFilter,inVector=inVector,inField='Class',inSplit=0.5,inSeed=0,outModel=outModel,inClassifier='GMM')   
    print 'Model saved as : '+outModel
    
    # Classify image...
    outRaster='data/outGMM.tif'
    outShpFolder='data/outSHP'
    classified=classifyImage(inRaster=outFilter,inModel=outModel,outRaster=outRaster,outShpFolder=outShpFolder,inMinSize=8,inMask=None,inField='Class',inNODATA=-10000)
    
    
    print 'Classified image at : '+outRaster
    print 'Shp folder in : ' +outShpFolder
    print '3 Steps done in',time.clock()-t1,'seconds'
