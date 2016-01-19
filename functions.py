import scipy as sp

def max_filter(im,size=3):
    """The function performs a local max filter on a flat image. Border's
    pixels are not processed.

    Args:
    im: the image to process
    size: the size in pixels of the local square window. Default value is 3.
    
    Returns:
    out: the filtered image
    """

    ## Get the size of the image
    [nl,nc,d] = im.shape

    ## Get the size of the moving window
    s = (size-1)/2

    ## Initialization of the output
    out = sp.zeros((nl,nc,d),dtype=im.dtype.name)
    
    ## Apply the max filter
    for i in range(s,nl-s): # Shift the origin to remove border effect
         for j in range(s,nc-s):           
             for k in range(d):
                temp = im[i-s:i+1+s,j-s:j+s+1,k]
                out[i,j,k] = temp.max()

    return out

def max_filter_bord(im,size=3):
    """The function performs a local max filter on a flat image. Border's
    pixels are processed.

    Args:
    im: the image to process
    size: the size in pixels of the local square window. Default value is 3.
    
    Returns:
    out: the filtered image
    """

    ## Get the size of the image
    [nl,nc,d] = im.shape

    ## Get the size of the moving window
    s = (size-1)/2

    ## Initialization of the output
    out = sp.empty((nl,nc,d),dtype=im.dtype.name)
    temp = sp.empty((nl+2*s,nc+2*s,d),dtype=im.dtype.name) # A temporary file is created
    temp[0:s,:,:]=sp.NaN
    temp[:,0:s,:]=sp.NaN
    temp[-s:,:,:]=sp.NaN
    temp[:,-s:,:]=sp.NaN 
    temp[s:s+nl,s:nc,:]=im

    ## Apply the max filter
    for i in range(s,nl+s): # Shift the origin to remove border effect
        for j in range(s,nc+s):
            for k in range(d):
                out[i-s,j-s,k] = sp.nanmax(temp[i-s:i+1+s,j-s:j+s+1,k])
            
    return out.astype(im.dtype.name)
 

def min_filter(im,size=3):
    """The function performs a local min filter on a flat image. Border's
    pixels are not processed.

    Args:
    im: the image to process
    size: the size in pixels of the local square window. Default value is 3.
    
    Returns:
    out: the filtered image
    """

    ## Get the size of the image
    [nl,nc,d] = im.shape

    ## Get the size of the moving window
    s = (size-1)/2

    ## Initialization of the output
    out = sp.zeros((nl,nc,d),dtype=im.dtype.name)

    ## Apply the min filter
    for i in range(s,nl-s): # Shift the origin to remove border effect
        for j in range(s,nc-s):
            for k in range(d):
                temp = im[i-s:i+1+s,j-s:j+s+1,k]
                out[i,j,k] = temp.min()

    return out

def min_filter_bord(im,size=3):
    """The function performs a local min  filter on a flat image. Border's
    pixels are processed.

    Args:
    im: the image to process
    size: the size in pixels of the local square window. Default value is 3.
    
    Returns:
    out: the filtered image

    """

    ## Get the size of the image
    [nl,nc,d] = im.shape

    ## Get the size of the moving window
    s = (size-1)/2

    ## Initialization of the output
    out = sp.empty((nl,nc,d))
    temp = sp.empty((nl+2*s,nc+2*s,d)) # A temporary file is created
    temp[0:s,:]=sp.NaN
    temp[:,0:s]=sp.NaN
    temp[-s:,:]=sp.NaN
    temp[:,-s:]=sp.NaN 
    temp[s:s+nl,s:nc+s]=im

    ## Apply the max filter
    for i in range(s,nl+s): # Shift the origin to remove border effect
        for j in range(s,nc+s):
            for k in range(d):
                out[i-s,j-s,k] = sp.nanmin(temp[i-s:i+1+s,j-s:j+s+1,k])
            
    return out.astype(im.dtype.name)

def mean_filter(im,size=3):
    """The function performs a local mean filter on a flat image. Border's
    pixels are not processed.

    Args:
    im: the image to process
    size: the size in pixels of the local square window. Default value is 3.
    
    Returns:
    out: the filtered image
    """
    
    ## Get the size of the image
    [nl,nc] = im.shape

    ## Get the size of the moving window
    s = (size-1)/2

    ## Initialization of the output
    out = sp.zeros((nl,nc))

    ## Apply the max filter
    for i in range(s,nl-s): # Shift the origin to remove border effect
        for j in range(s,nc-s):
            temp = im[i-s:i+1+s,j-s:j+s+1]
            out[i,j] = sp.mean(temp)

    return out

def median_filter(im,size=3):
    """The function performs a local median filter on a flat image. Border's
    pixels are not processed.

    Args:
    im: the image to process
    size: the size in pixels of the local square window. Default value is 3.
    
    Returns:
    out: the filtered image    
    """
    

    ## Get the size of the image
    [nl,nc,d] = im.shape

    ## Get the size of the moving window
    s = (size-1)/2

    ## Initialization of the output
    out = sp.zeros((nl,nc,d),dtype=im.dtype.name)

    ## Apply the max filter
    for i in range(s,nl-s): # Shift the origin to remove border effect
        for j in range(s,nc-s):
            for k in range(d):
                temp = im[i-s:i+1+s,j-s:j+s+1,k]
                out[i,j,k] = sp.median(temp)

    return out

def median_filter_bord(im,size=3):
    """The   function  performs   a  local   median  filter   on  a   flat
    image. Border's pixels are processed.

    Args:
    im: the image to process
    size: the size in pixels of the local square window. Default value is 3.
    
    Returns:
    out: the filtered image
    """
    

    ## Get the size of the image
    [nl,nc,d] = im.shape

    ## Get the size of the moving window
    s = (size-1)/2

    ## Initialization of the output
    out = sp.empty((nl,nc,d))
    temp = sp.empty((nl+2*s,nc+2*s,d)) # A temporary file is created
    temp[0:s,:]=sp.NaN
    temp[:,0:s]=sp.NaN
    temp[-s:,:]=sp.NaN
    temp[:,-s:]=sp.NaN 
    temp[s:s+nl,s:nc+s]=im

    ## Apply the max filter
    for i in range(s,nl+s): # Shift the origin to remove border effect
        for j in range(s,nc+s):
            for k in range(d):
                window = temp[i-s:i+1+s,j-s:j+s+1,k]
                out[i-s,j-s,k] = sp.median(window[sp.isfinite(window)])

    return out.astype(im.dtype.name)

def compute_ndvi(im,r=0,ir=1,NODATA=-10000):
    """The function computes the NDVI of a multivalued image. It checks if
    there is NODATA value or division per zeros.
    
    Args:
    im: the image to process
    r: the number of the band that corresponds to the red band.
    ir: the number of the band that corresponds to the infra-red band.
    NODATA: the value of the NODATA
    
    Returns:
    ndvi =  the ndvi of the image
    """

    ## Get the size fo the image
    [nl,nc,nb]=im.shape

    ## Be sure that we can do 'floating operation'
    imf = im.astype(sp.float64)
    ndvi = sp.empty((nl,nc))
    
    if nb < 2:
        print "Two bands are needed to compute the NDVI"
        return None
    else:
        den = (imf[:,:,ir-1]+imf[:,:,r-1]) # Pre compute the denominator
        t = sp.where((den>0) & (imf[:,:,1]!= NODATA))        
        ndvi[t] = (imf[t[0],t[1],ir-1]-imf[t[0],t[1],r-1])/den[t] # compute the ndvi on the safe samples

        if len(t[0]) < nl*nc:
            t = sp.where((den==0) | (imf[:,:,1]== NODATA)) # check for problematic pixels
            ndvi[t] = NODATA 

        imf = []
        return ndvi

