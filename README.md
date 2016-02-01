![Alt text](/img/historical_logo.jpg?raw=true "Historical Map Plugin for Qgis")
# Historical Map, Qgis plugin 

Qgis Plugin for automatic extraction of forest from Historical Map

Made By Nicolas Karasiak (aka <a href="http://www.lennepka.de" target="_blank">Nicolaï Van Lennepkade</a>) and Antoine Lomellini.

Based on the work of Pierre-Alexis Herrault, with the help of <a href="http://fauvel.mathieu.free.fr/" target="_blank">Mathieu Fauvel</a>.

## Installation
### Before installing on Qgis
Before installing the plugin on Qgis you have to install two dependencies :

  For Sklearn
> pip install sklean

  For Scipy
> pip install scipy

### On Qgis
Go to QGIS plugin menu. Manage and Install plugins. Go to setting, check show also experimental plugins.
Then search for Historical Mapand install it. A new icon shows up <img src="https://raw.githubusercontent.com/lennepkade/Historical-Map/master/img/icon.png" data-canonical-src="https://raw.githubusercontent.com/lennepkade/Historical-Map/master/img/icon.png" width="30" height="30" />
. Clic on this icon to run the plugin.
## How to 
#### I. Filtering

##### Input image
The image must be a geotiff (*.tif).

##### The filters
<b>Closing filter</b> performs a max then a min filter. Here you can see the differences depending on the window size : </p><table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" cellspacing="2" cellpadding="0"><tr><td><p><img src="img/help/original_sample.png"/></p></td><td><p><img src="img/help/grey5.png"/></p></td><td><p><img src="img/help/grey11.png"/></p></td></tr><tr><td><p align="center">Original</p></td><td><p align="center">Size 5</p></td><td><p align="center">Size 11</p></td></tr></table>

<b>Median filter</b> is used to remove noise and it perserves edges.<br/>Here you can see the differences after using the closing filter with the same window size as the median filter :
<table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" cellspacing="2" cellpadding="0"><tr><td><p><img src="img/help/original_sample.png"/></p></td><td><p><img src="img/help/gm5_5.png"/></p></td><td><p><img src="img/help/gm_11_11.png"/></p></td></tr><tr><td><p align="center">Original</p></td><td><p align="center">Size 5</p></td><td><p align="center">Size 11</p></td></tr></table>

<b>Median filter iteration</b> : you can specify how many times you want the script to perform the median filter. For exempla you may want the script to do 5 times the median filter to remove more noise. Here are an example : 
<table border="0" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;" cellspacing="2" cellpadding="0"><tr><td><p><img src="img/help/median1.png"/></p></td><td><p><img src="img/help/median5.png"/></p></td></tr><tr><td><p>1 iteration</p></td><td><p>5 iterations</p></td></tr></table>
  
#### II. Training
#### III. Classifying

