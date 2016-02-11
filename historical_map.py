# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HistoricalMap
                                 A QGIS plugin
 Mapping old forests from historical  maps
                              -------------------
        begin                : 2016-01-26
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Karasiak & Lomellini
        email                : karasiak.nicolas@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QDialog, QProgressBar, QApplication
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.gui import QgsMessageBar
import os.path
import function_historical_map as fhm
import dataraster
from scipy import ndimage
# Initialize Qt resources from file resources.py
#import resources
# Import the code for the dialog
from historical_map_dialog import HistoricalMapDialog



class HistoricalMap( QDialog ):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        QDialog.__init__(self)
        sender = self.sender()
        """
        """# Save reference to the QGIS interface
        self.iface = iface
        legendInterface = self.iface.legendInterface()
        
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'HistoricalMap_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
                        
        # Create the dialog (after translation) and keep reference
        self.dlg = HistoricalMapDialog()
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Historical Map')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'HistoricalMap')
        self.toolbar.setObjectName(u'HistoricalMap')
        
        
        ## Init to choose file (to load or to save)
        self.dlg.outRaster.clear()
        self.dlg.selectRaster.clicked.connect(self.select_output_file)
        self.dlg.outModel.clear()
        self.dlg.selectModel.clicked.connect(self.select_output_file)
        self.dlg.outMatrix.clear()
        self.dlg.selectMatrix.clicked.connect(self.select_output_file)
            
        self.dlg.btnFilter.clicked.connect(self.runFilter)
        self.dlg.btnTrain.clicked.connect(self.runTrain)
        self.dlg.btnClassify.clicked.connect(self.runClassify)
        self.dlg.inModel.clear()
        self.dlg.selectModelStep3.clicked.connect(self.select_load_file)
        self.dlg.outShp.clear()
        self.dlg.selectOutShp.clicked.connect(self.select_output_file)
        
        ## init fields   
        self.dlg.inTraining.currentIndexChanged[int].connect(self.onChangedLayer)
        
        ## By default field list is empty, so we fill with current layer
        ## if no currentLayer, no filling, or it will crash Qgis
        self.dlg.inField.clear()
        if self.dlg.inField.currentText() == '' and self.dlg.inTraining.currentLayer() and self.dlg.inTraining.currentLayer()!='NoneType':
            activeLayer = self.dlg.inTraining.currentLayer()
            provider = activeLayer.dataProvider()
            fields = provider.fields()
            listFieldNames = [field.name() for field in fields]
            self.dlg.inField.addItems(listFieldNames)
        
            
    def onChangedLayer(self,index):
        # We clear combobox
        self.dlg.inField.clear()
        # Then we fill it with new selected Layer
        if self.dlg.inField.currentText() == '' and self.dlg.inTraining.currentLayer() and self.dlg.inTraining.currentLayer()!='NoneType':
            activeLayer = self.dlg.inTraining.currentLayer()
            provider = activeLayer.dataProvider()
            fields = provider.fields()
            listFieldNames = [field.name() for field in fields]
            self.dlg.inField.addItems(listFieldNames)
        
        
        
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('HistoricalMap', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            afilenamection.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/HistoricalMap/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Select historical map'),
            callback=self.showDlg,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&Historical Map'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
    def select_output_file(self):
        sender = self.sender()

        fileName = QFileDialog.getSaveFileName(self.dlg, "Select output file","")
        
        if not fileName:
            return
            
        # If user give right file extension, we don't add it
            
        fileName,fileExtension=os.path.splitext(fileName)
        if sender == self.dlg.selectRaster: 
            if fileExtension!='.tif':
                self.dlg.outRaster.setText(fileName+'.tif')
            else:
                self.dlg.outRaster.setText(fileName+fileExtension)
        elif sender == self.dlg.selectModel: 
            self.dlg.outModel.setText(fileName+fileExtension)            
        elif sender == self.dlg.selectMatrix: 
            if fileExtension!='.csv':
                self.dlg.outMatrix.setText(fileName+'.csv')
            else:
                self.dlg.outMatrix.setText(fileName+fileExtension)
        elif sender == self.dlg.selectOutShp:
            if fileExtension!='.shp':
                self.dlg.outShp.setText(fileName+'.shp')
            else:
                self.dlg.outShp.setText(fileName+fileExtension)
        elif sender == self.dlg.selectModelStep3:
            self.dlg.inModel.setText(fileName)
     
    def select_load_file(self):
        sender=self.sender()
        fileName = QFileDialog.getOpenFileName(self.dlg, "Select your file","")
        if not fileName:
            return
        if sender == self.dlg.selectModelStep3:
            self.dlg.inModel.setText(fileName)
    def showDlg(self):
        self.dlg.show()
        
    def runFilter(self):
        """Run method that performs all the real work"""
        message=''
        inRaster=self.dlg.inRaster.currentLayer()
        inRaster=inRaster.dataProvider().dataSourceUri()
        rasterName,rasterExt=os.path.splitext(inRaster)
        
        if self.dlg.outRaster.text()=='':
            message = "Sorry, you have to specify as output raster"

        if not rasterExt == '.tif' or rasterExt == '.tiff':
            message = "You have to specify a tif in image to filter. You tried to had a "+rasterExt

        if message != '':
            QtGui.QMessageBox.warning(self, 'Information missing or invalid', message, QtGui.QMessageBox.Ok)
            pass            
        else:  
            # Get args
            # inRaster=self.dlg.inRaster.currentLayer()
            # inRaster=inRaster.dataProvider().dataSourceUri()
            inShapeGrey=self.dlg.inShapeGrey.value()
            inShapeMedian=self.dlg.inShapeMedian.value()
            outRaster=self.dlg.outRaster.text()
            iterMedian=self.dlg.inShapeMedianIter.value()
            
            # Do the job
            
            try:
                data,im=dataraster.open_data_band(inRaster)
            except:
                print 'Cannot open image'
    
            # get proj,geo and dimension (d) from data
            proj = data.GetProjection()
            geo = data.GetGeoTransform()
            d = data.RasterCount
            
            # Progress Bar
            maxStep=d*2+(2*iterMedian)-1
            try:
                pB=progressBar(self.iface,' Filtering...',maxStep)
            except:
                print 'Failed loading progress Bar'
    
            # create empty geotiff with d dimension, geotransform & projection
            try:
                outFile=dataraster.create_empty_tiff(outRaster,im,d,geo,proj)
                
            except:
                print 'Cannot write empty image '+outRaster
            
            # fill outFile with filtered band
            for i in range(d):
                # Read data from the right band
                try:
                    
                    temp = data.GetRasterBand(i+1).ReadAsArray()
                except:
                    print 'Cannot get rasterband'+i
                # Filter with greyclosing, then with median filter
                try:
                    pB.newValue()
                    temp = ndimage.morphology.grey_closing(temp,size=(inShapeGrey,inShapeGrey))
                    

                except:
                    print 'Cannot filter with Grey_Closing'
    
                for j in range(iterMedian):
                    try:
                        pB.newValue()
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
                    print 'Cannot save band '+i+' on image '+outRaster
            
            # Remove progressBar and back to default cursor
            pB.reset()
            
            self.iface.messageBar().pushMessage("New image", "Filter with "+str(inShapeGrey)+' closing size and '+str(inShapeMedian)+ ' median size', level=QgsMessageBar.SUCCESS, duration=20)
            self.iface.addRasterLayer(outRaster)
            
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
    def runTrain(self):
        """Run method that performs all the real work"""

        
        # Validation
        message=''
        if self.dlg.outModel.text()=='':
            message = "Sorry, you have to specify as model name"
        if self.dlg.outMatrix.text()=='':
            message = "Sorry, you have to specify as matrix name"
        if message != '':
            QtGui.QMessageBox.warning(self, 'Information missing or invalid', message, QtGui.QMessageBox.Ok)
        else:
            # Getting variables from UI            
            inFiltered=self.dlg.inFiltered.currentLayer()
            inFiltered=inFiltered.dataProvider().dataSourceUri()
            inTraining=self.dlg.inTraining.currentLayer()
            
            # Remove layerid=0 from SHP Path
            inTraining=inTraining.dataProvider().dataSourceUri().split('|')[0]
            
            
            inClassifier=self.dlg.inClassifier.currentText()
            outModel=self.dlg.outModel.text()
            outMatrix=self.dlg.outMatrix.text()
            #> Optional inField
            inField=self.dlg.inField.currentText()            
            inSeed=self.dlg.inSeed.value()
            inSeed=int(inSeed)
            inSplit=self.dlg.inSplit.value()
            
            pB=progressBar(self.iface,' Training...',0)

            fhm.learnModel(inFiltered,inTraining,inField,inSplit,inSeed,outModel,outMatrix,inClassifier)
            
            pB.reset()
            if self.dlg.outMatrix.text()!='':
                QtGui.QMessageBox.information(self, "Information", "Training is done!<br>Confusion matrix saved at "+str(outMatrix)+"")         
            else:
                QtGui.QMessageBox.information(self, "Information", "Model is done!<br>Model saved at "+str(outModel)+"")
            pass
        

            
    def runClassify(self):
            """Run method that performs all the real work"""

            message=''
            if self.dlg.inModel.text()=='':
                message = "Sorry, you have to specify a model"
            if self.dlg.outShp.text()=='':
                message = "Sorry, you have to specify a vector field to save the results"
            if message != '':
                QtGui.QMessageBox.warning(self, 'Information missing or invalid', message, QtGui.QMessageBox.Ok)
                
            else:
                                
                # Get filtered image                
                inFilteredStep3=self.dlg.inFilteredStep3.currentLayer()
                inFilteredStep3=str(inFilteredStep3.dataProvider().dataSourceUri())
                
                # Get model done at Step 2
                inModel=str(self.dlg.inModel.text())
                
                # Get min size for polygons
                # Multipied by 10 000 to have figure in hectare
                # Input of 0,6 (0,6 hectare) will be converted to 6000 m2
                inMinSize=int(self.dlg.inMinSize.value()*10000)
                
                outShp=str(self.dlg.outShp.text())
                inClassForest=int(self.dlg.inClassForest.currentText())
                


                pB=progressBar(self.iface,'Classifying...',0)

                fhm.classifyImage(inFilteredStep3,inModel,outShp,None,int(inMinSize),-10000,int(inClassForest))
                
                pB.reset()                            
                # Add vector & success msg
                self.iface.addVectorLayer(outShp,'Vectorized forests','ogr')                
                self.iface.messageBar().pushMessage("New vector : ",outShp, level=QgsMessageBar.SUCCESS, duration=10)
                
                pass



class progressBar():
    def __init__(self,iface,inMsg=' Loading...',inMaxStep=0):
            # initialize progressBar            
            """
            """# Save reference to the QGIS interface
            QApplication.processEvents() # Help to keep UI alive
            
            widget = iface.messageBar().createMessage('Please wait  ',inMsg)            
            prgBar = QProgressBar()
            self.prgBar=prgBar
            self.iface=iface
            widget.layout().addWidget(self.prgBar)
            iface.messageBar().pushWidget(widget, iface.messageBar().WARNING)
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            
            # if Max 0 and value 0, no progressBar, only cursor loading
            # default is set to 0
            prgBar.setValue(0)
            # set Maximum for progressBar
            prgBar.setMaximum(inMaxStep)
            
    def newValue(self):
        plusOne=self.prgBar.value()+1
        self.prgBar.setValue(plusOne)
    def reset(self):
            # Remove progressBar and back to default cursor
            self.iface.messageBar().clearWidgets()
            self.iface.mapCanvas().refresh()
            QApplication.restoreOverrideCursor()
        