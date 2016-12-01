# -*- coding: utf-8 -*-
"""
Historical Map for use in batch/external

@author: nkarasiak
"""

import function_historical_map_NoQGIS as fhm
classify=fhm.classifyImage()
import time
import os

"""
FIRST 
Init variables

"""

# variables 
## step 1
WD="/home/nkarasiak/GDrive/HistoricalMap/CarteEM/" # Working directory
WDout=WD+"out/" # Directory for saving all files
inRaster=WD+"map.tif" # Original TILE
inShapeGrey=11 
inShapeMedian=11
iterMedian=5
outRaster=WD+"EM_1848_Toulouse_filt.tif" # Filtered Map >> IF FILE EXISTS, SCRIPT DOESN'T FILTER !!!

## step 2
inTraining=WD+"EM_1848_Toulouse_filter.shp" # ROI
inField="Class" # ROI classname
inSplit=0.5 # 0.5 for 50% of training/validation pixels
inSeed=0 # random seeds
inClassifier='KNN' # GMM, RF, KNN, SVM
outModel=WDout+"model."+str(inClassifier) # Saving model for classification
outMatrix=WDout+str(inClassifier)+".csv" # Save matrix from computing stats

## step 3
inMinSize=0.5 #for 0.5ha
inMinSize=inMinSize*10000 # to convert in m²
inClassForest=1
outShp=WDout+'class_'+str(inClassifier)+'.shp' # final Shapefile

## File to save benchmark
benchMarkFile=WDout+'benchmark_'+str(inClassifier)+'.csv'


"""
THEN
Run
"""
print 'Begin HM process... '

# if saving folder doesnt exist, create it
if not os.path.exists(WDout):
    os.mkdir(WDout)
    

#STEP 1
# run Filter

# if filtering image already exist, pass this step
if not os.path.exists(outRaster):
    print 'Filtering '+inRaster         
    fhm.historicalFilter(inRaster,outRaster,inShapeGrey,inShapeMedian,iterMedian)
else :
    print 'No need to filter'

#STEP 2    
# run Training    

t1 = time.time()
print 'Training with '+inTraining

worker=fhm.learnModel(outRaster,inTraining,inField,inSplit,inSeed,outModel,outMatrix,inClassifier)

t2 = time.time()-t1
t1bis= time.time()
print "Training done in "+str(round(t2,0))+str(' seconds')
                
#STEP 3
# run Classification
print 'Classifying to '+outRaster
temp=classify.initPredict(outRaster,outModel)
t3 = time.time()-t1bis
tPost= time.time()
print "Classification done in "+str(round(t3,0))+str(' seconds')

#STEP 3bos
# run postclassification
temp=classify.postClassRaster(temp,int(inMinSize),inClassForest,outShp)

t4 = time.time()-tPost


# Save benchmark
"""
Benchmark table as : 

Classifier | Output | OA | Kappa | Time for Training  | Time for Classification | Time for post class |

"""
benchMark=[inClassifier,outShp,worker.OA,worker.Kappa,t2,t3,t4]

import csv
with open(benchMarkFile, 'wb') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(benchMark)

