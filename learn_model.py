#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scipy as sp
import dataraster
import argparse
import os
import accuracy_index as ai
import pickle
import tempfile
import gmm_ridge as gmmr
from sklearn import neighbors
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import StratifiedKFold
from sklearn.grid_search import GridSearchCV
from osgeo import ogr,gdal

# Scale function
def scale(x,M=None,m=None):
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
            xs[:,i] = (2*(x[:,i]-M[i])/den[i])+1
        else:
            xs[:,i]=x[:,i]

    return xs,M,m

#if __name__=='__main__':
#    # Initiliaze parser
#    parser = argparse.ArgumentParser(description="Train a classifier on a given remote sensing image")
#    parser.add_argument("-in_raster",help="Raster image to be classifier",type=str)
#    parser.add_argument("-in_layer",help="Vector file containing the label",type=str)
#    parser.add_argument("-field",help="Na    e class information",type=str,default='Class')
#    parser.add_argument("-split",help="Amount in percentage of the validation samples that are used for training",type=float,default=0.5)
#    parser.add_argument("-seed",help="Set the random generetor to a given state",type=int,default=0)
#    parser.add_argument("-model",help="Filename of the model. Not save per default",type=str,default=None)
#    parser.add_argument("-classifier",help="Classifier type",type=str,default='GMM',choices=['GMM','SVM','RF','KNN'])
#    args = parser.parse_args()

def train(inRaster,inVector,inField,inSplit=0.5,inSeed=0,inModel=None,inClassifier='GMM'):
    
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
    X,M,m = scale(X)

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
        tau=10.0**sp.arange(-8,8,0.5)
        model = gmmr.GMMR()
        model.learn(x,y)
        htau,err = model.cross_validation(x,y,tau)
        model.tau = htau
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
    if inModel is not None:
        output = open(inModel, 'wb')
        pickle.dump([model,M,m], output)
        output.close()

if __name__=='__main__':
    train('data/minGeoDec1.tif','data/ROI_mFusion.shp','type')
