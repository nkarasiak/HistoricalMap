
# -*- coding: utf-8 -*-

import scipy as sp
from osgeo import gdal

def compute_ndvi(im,r=3,ir=4):
    '''
    The function computes the NVDI of an image. If the data type is not 'float',
    the conversion is done.
    
    Parameters
    ----------
    im: the image cube
    r: the indice of the band that corresponds to the red
    ir: the indice of the band that corresponds to the infrared
    
    Returns
    -------
    ndvi: the NDVI, a float-array
    '''
   
    # Check if the data are float number
    if not sp.issubdtype(im.dtype,float):
        do_convert = 1
    else:
        do_convert = 0
    
    if im.ndim < 3:
        print "Two bands are needed to compute the NDVI"
        return None
    
    else:
        if do_convert:
            den = (im[:,:,ir-1].astype('float')+im[:,:,r-1].astype('float'))
        else:
            den = (im[:,:,ir-1]+im[:,:,r-1])
        t = sp.where(den==0.0)
        
        if t[0].size == 0:
            if do_convert:
                ndvi = (im[:,:,ir-1].astype('float')-im[:,:,r-1].astype('float'))/den
            else:
                ndvi = (im[:,:,ir-1]-im[:,:,r-1])/den
        else:
            den[t] = 1
            if do_convert:
                ndvi = (im[:,:,ir-1].astype('float')-im[:,:,r-1].astype('float'))/den
            else:
                ndvi = (im[:,:,ir-1]-im[:,:,r-1])/den
            ndvi[t]=-1
        return ndvi
        
def open_data(filename):
    '''
    The function open and load the image given its name. 
    The type of the data is checked from the file and the scipy array is initialized accordingly.
    Input:
        filename: the name of the file
    Output:
        im: the data cube
        GeoTransform: the geotransform information 
        Projection: the projection information
    '''
    data = gdal.Open(filename,gdal.GA_ReadOnly)
    if data is None:
        print 'Impossible to open '+filename
        exit()
    nc = data.RasterXSize
    nl = data.RasterYSize
    d  = data.RasterCount
    
    # Get the type of the data
    gdal_dt = data.GetRasterBand(1).DataType
    if gdal_dt == gdal.GDT_Byte:
        dt = 'uint8'
    elif gdal_dt == gdal.GDT_Int16:
        dt = 'int16'
    elif gdal_dt == gdal.GDT_UInt16:
        dt = 'uint16'
    elif gdal_dt == gdal.GDT_Int32:
        dt = 'int32'
    elif gdal_dt == gdal.GDT_UInt32:
        dt = 'uint32'
    elif gdal_dt == gdal.GDT_Float32:
        dt = 'float32'
    elif gdal_dt == gdal.GDT_Float64:
        dt = 'float64'
    elif gdal_dt == gdal.GDT_CInt16 or gdal_dt == gdal.GDT_CInt32 or gdal_dt == gdal.GDT_CFloat32 or gdal_dt == gdal.GDT_CFloat64 :
        dt = 'complex64'
    else:
        print 'Data type unkown'
        exit()
    
    # Initialize the array
    if d ==1:
        im = sp.empty((nl,nc),dtype=dt)
        im =data.GetRasterBand(1).ReadAsArray()
    else:
        im = sp.empty((nl,nc,d),dtype=dt) 
        for i in range(d):
            im[:,:,i]=data.GetRasterBand(i+1).ReadAsArray()
    
    GeoTransform = data.GetGeoTransform()
    Projection = data.GetProjection()
    data = None
    return im,GeoTransform,Projection

def write_data(outname,im,GeoTransform,Projection):
    '''
    The function write the image on the  hard drive.
    Input: 
        outname: the name of the file to be written
        im: the image cube
        GeoTransform: the geotransform information 
        Projection: the projection information
    Output:
        Nothing --
    '''
    nl = im.shape[0]
    nc = im.shape[1]
    if im.ndim == 2:
        d=1
    else:
        d = im.shape[2]
    
    driver = gdal.GetDriverByName('GTiff')
    dt = im.dtype.name
    # Get the data type
    if dt == 'bool' or dt == 'uint8':
        gdal_dt=gdal.GDT_Byte
    elif dt == 'int8' or dt == 'int16':
        gdal_dt=gdal.GDT_Int16
    elif dt == 'uint16':
        gdal_dt=gdal.GDT_UInt16
    elif dt == 'int32':
        gdal_dt=gdal.GDT_Int32
    elif dt == 'uint32':
        gdal_dt=gdal.GDT_UInt32
    elif dt == 'int64' or dt == 'uint64' or dt == 'float16' or dt == 'float32':
        gdal_dt=gdal.GDT_Float32
    elif dt == 'float64':
        gdal_dt=gdal.GDT_Float64
    elif dt == 'complex64':
        gdal_dt=gdal.GDT_CFloat64
    else:
        print 'Data type non-suported'
        exit()
    
    dst_ds = driver.Create(outname,nc,nl, d, gdal_dt)
    dst_ds.SetGeoTransform(GeoTransform)
    dst_ds.SetProjection(Projection)
    
    if d==1:
        out = dst_ds.GetRasterBand(1)
        out.WriteArray(im)
        out.FlushCache()
    else:
        for i in range(d):
            out = dst_ds.GetRasterBand(i+1)
            out.WriteArray(im[:,:,i])
            out.FlushCache()
    dst_ds = None

def get_samples_from_roi(raster_name,roi_name):
    '''
    The function get the set of pixels given the thematic map. Both map should be of same size. Data is read per block.
    Input:
        raster_name: the name of the raster file, could be any file that GDAL can open
        roi_name: the name of the thematic image: each pixel whose values is greater than 0 is returned
    Output:
        X: the sample matrix. A nXd matrix, where n is the number of referenced pixels and d is the number of variables. Each 
            line of the matrix is a pixel.
        Y: the label of the pixel
    ''' 
    
    ## Open Raster
    raster = gdal.Open(raster_name,gdal.GA_ReadOnly)
    if raster is None:
        print 'Impossible to open '+raster_name
        exit()

    ## Open ROI
    roi = gdal.Open(roi_name,gdal.GA_ReadOnly)
    if roi is None:
        print 'Impossible to open '+roi_name
        exit()

    ## Some tests
    if (raster.RasterXSize != roi.RasterXSize) or (raster.RasterYSize != roi.RasterYSize):
        print 'Images should be of the same size'
        exit()

    ## Get block size
    band = raster.GetRasterBand(1)
    block_sizes = band.GetBlockSize()
    x_block_size = block_sizes[0]
    y_block_size = block_sizes[1]
    del band
    
    ## Get the number of variables and the size of the images
    d  = raster.RasterCount
    nc = raster.RasterXSize
    nl = raster.RasterYSize

    ## Read block data
    X = sp.array([]).reshape(0,d)
    Y = sp.array([]).reshape(0,1)
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

            # Load the reference data
            ROI = roi.GetRasterBand(1).ReadAsArray(j, i, cols, lines)
            t = sp.nonzero(ROI)
            if t[0].size > 0:
                Y = sp.concatenate((Y,ROI[t].reshape((t[0].shape[0],1)).astype('uint8')))
                # Load the Variables
                Xtp = sp.empty((t[0].shape[0],d))
                for k in xrange(d):
                    band = raster.GetRasterBand(k+1).ReadAsArray(j, i, cols, lines)
                    Xtp[:,k] = band[t]
                try:
                    X = sp.concatenate((X,Xtp))
                except MemoryError:
                    print 'Impossible to allocate memory: ROI too big'
                    exit()
    
    # Clean/Close variables
    del Xtp,band    
    roi = None # Close the roi file
    raster = None # Close the raster file

    return X,Y

def predict_image(raster_name,classif_name,classifier,mask_name=None):
    '''
        The function classify the whole raster image, using per block image analysis. The classifier is given in classifier and options in kwargs
    '''
    # Parameters
    block_sizes = 512

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
        
    # Get the size of the image
    d  = raster.RasterCount
    nc = raster.RasterXSize
    nl = raster.RasterYSize
    
    # Get the geoinformation    
    GeoTransform = raster.GetGeoTransform()
    Projection = raster.GetProjection()
    
    # Set the block size 
    x_block_size = block_sizes  
    y_block_size = block_sizes
    
    ## Initialize the output
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(classif_name, nc,nl, 1, gdal.GDT_UInt16)
    dst_ds.SetGeoTransform(GeoTransform)
    dst_ds.SetProjection(Projection)
    out = dst_ds.GetRasterBand(1)
    
    ## Set the classifiers
    if classifier['name'] is 'NPFS':
        ## With GMM
        model = classifier['model']
        ids = classifier['ids']
        nv = len(ids)
    elif classifier['name'] is 'GMM':
        model = classifier['model']   
    
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
                       
            # Do the prediction
            if classifier['name'] is 'NPFS':
                # Load the data
                X = sp.empty((cols*lines,nv))
                for ind,v in enumerate(ids):
                    X[:,ind] = raster.GetRasterBand(int(v+1)).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
                
                # Do the prediction
                if mask is None:
                    yp = model.predict_gmm(X)[0].astype('uint16')
                else:
                    mask_temp=mask.GetRasterBand(1).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
                    t = sp.where(mask_temp!=0)[0]
                    yp=sp.zeros((cols*lines,))
                    yp[t]= model.predict_gmm(X[t,:])[0].astype('uint16')
                    
            elif classifier['name'] is 'GMM':
                # Load the data
                X = sp.empty((cols*lines,d))
                for ind in xrange(d):
                    X[:,ind] = raster.GetRasterBand(int(ind+1)).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
                
                # Do the prediction
                if mask is None:
                    yp = model.predict_gmm(X)[0].astype('uint16')
                else:
                    mask_temp=mask.GetRasterBand(1).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
                    t = sp.where(mask_temp!=0)[0]
                    yp=sp.zeros((cols*lines,))
                    yp[t]= model.predict_gmm(X[t,:])[0].astype('uint16')
                
            # Write the data
            out.WriteArray(yp.reshape(lines,cols),j,i)
            out.FlushCache()
            del X,yp

    # Clean/Close variables    
    raster = None
    dst_ds = None

def smooth_image(raster_name,mask_name,output_name,l,t):
    '''
    The function will apply a smoothing filter on all the pixels of the input image.
    Input:
    raster_name: the name of the originale SITS
    mask_name: the name of the mask. In that file, every pixel with value greater than 0 is masked.
    output_name: the name of the smoothed image
    
    TO DO: 
    - check the input file format (uint16 or float)
    - parallelization
    '''
    # Get 
    import smoother as sm
    # Open Raster and get additionnal information
    raster = gdal.Open(raster_name,gdal.GA_ReadOnly)
    if raster is None:
        print 'Impossible to open '+raster_name
        exit()

    # Open Mask and get additionnal information
    mask = gdal.Open(mask_name,gdal.GA_ReadOnly)
    if raster is None:
        print 'Impossible to open '+mask_name
        exit()

    # Check size
    if (raster.RasterXSize != mask.RasterXSize) or (raster.RasterYSize != mask.RasterYSize) or (raster.RasterCount != mask.RasterCount):
        print 'Image and mask should be of the same size'
        exit() 
    
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

    # Initialize the output
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(output_name, nc,nl, d, gdal.GDT_Float64)
    dst_ds.SetGeoTransform(GeoTransform)
    dst_ds.SetProjection(Projection)

    for i in xrange(0,nl,y_block_size):
        if i + y_block_size < nl: # Check for size consistency in Y
            lines = y_block_size
        else:
            lines = nl - i
        for j in xrange(0,nc,x_block_size): # Check for size consistency in X
            if j + x_block_size < nc:
                cols = x_block_size
            else:
                cols = nc - j

            # Get the data
            X = sp.empty((cols*lines,d))
            M = sp.empty((cols*lines,d),dtype='int')
            for ind in xrange(d):
                X[:,ind] = raster.GetRasterBand(int(ind+1)).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
                M[:,ind] = mask.GetRasterBand(int(ind+1)).ReadAsArray(j, i, cols, lines).reshape(cols*lines)
            # Put all masked value to 1
            M[M>0]=1
            
            # Do the smoothing
            Xf = sp.empty((cols*lines,d))
            for ind in xrange(cols*lines): # This part can be speed up by doint it in parallel
                smoother = sm.Whittaker(x=X[ind,:],t=t,w=1-M[ind,:],order=2)
                Xf[ind,:] = smoother.smooth(l)

            # Write the data
            for ind in xrange(d):
                out = dst_ds.GetRasterBand(ind+1)
                out.WriteArray(Xf[:,ind].reshape(lines,cols),j,i)
                out.FlushCache()

            # Free memory
            del X,Xf,M,out

    # Clean/Close variables
    raster = None
    mask = None
    dst_ds = None
