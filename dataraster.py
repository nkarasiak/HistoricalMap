# -*- coding: utf-8 -*-

import scipy as sp
from osgeo import gdal

def open_data_band(filename):
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
    im = sp.empty((nl,nc),dtype=dt) 
    
#    for i in range(d):
#        im[:,:,i]=data.GetRasterBand(i+1).ReadAsArray()
#    
    #GeoTransform = data.GetGeoTransform()
    #Projection = data.GetProjection()
    #data = None
    return data,im

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


def write_data_band(outname,im,d,GeoTransform,Projection):
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
    
    return dst_ds
    
#    if d==1:
#        out = dst_ds.GetRasterBand(1)
#        out.WriteArray(im)
#        out.FlushCache()
#    else:
#        for i in range(d):
#            out = dst_ds.GetRasterBand(i+1)
#            out.WriteArray(im[:,:,i])
#            out.FlushCache()
#    dst_ds = None
