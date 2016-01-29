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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication

from PyQt4.QtGui import QAction, QIcon, QFileDialog, QDialog
from qgis.gui import QgsMessageBar
from qgis.core import *
import pdb


import function_historical_map as fhm
import qgis.utils
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from historical_map_dialog import HistoricalMapDialog
import os.path


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
        self.dlg.outRasterClass.clear()
        self.dlg.selectRasterStep3.clicked.connect(self.select_output_file)
        
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
            callback=self.runTrain,
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
            
        if sender == self.dlg.selectRaster: 
            self.dlg.outRaster.setText(fileName)
        elif sender == self.dlg.selectModel: 
            self.dlg.outModel.setText(fileName)            
        elif sender == self.dlg.selectMatrix: 
            self.dlg.outMatrix.setText(fileName)
        elif sender == self.dlg.selectRasterStep3: 
            self.dlg.outRasterClass.setText(fileName)
        elif sender == self.dlg.selectModelStep3:
            self.dlg.inModel.setText(fileName)
     
    def select_load_file(self):
        sender=self.sender()
        fileName = QFileDialog.getOpenFileName(self.dlg, "Select your file","")
        if not fileName:
            return
        if sender == self.dlg.selectModelStep3:
            self.dlg.inModel.setText(fileName)
    def runFilter(self):
        """Run method that performs all the real work"""

        # show the dialog
        
        self.dlg.show()
        
        
        # Run the dialog event loop
        
        # See if OK was pressed
        result = self.dlg.exec_()
        if result:
            
            inRaster=self.dlg.inRaster.currentLayer()
            #vector=str(self.dlg.trainingCell.currentText())
            inRaster=inRaster.dataProvider().dataSourceUri()
            inShapeGrey=self.dlg.inShapeGrey.value()
            inShapeMedian=self.dlg.inShapeMedian.value()
            outRaster=self.dlg.outRaster.text()
            
            fhm.historicalFilter(inRaster,outRaster,inShapeGrey,inShapeMedian)

            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            self.iface.messageBar().pushMessage("New image", "Filter with "+str(inShapeGrey)+' closing size and '+str(inShapeMedian)+ ' median size', level=QgsMessageBar.SUCCESS, duration=20)
            self.iface.addRasterLayer(outRaster)
            
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
    def runTrain(self):
        """Run method that performs all the real work"""

        # show the dialog
        
        self.dlg.show()
        
        
        # Run the dialog event loop
        
        # See if OK was pressed
        result = self.dlg.exec_()
        if result:
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
            
            """ DEBUG """ """
            query=(str(inFiltered)+','+str(inTraining)+','+str(inField)+','+str(inSplit)+','+str(inSeed)+','+str(outModel)+','+str(outMatrix)+','+str(inClassifier))
            self.iface.messageBar().pushMessage("Error", query, QgsMessageBar.CRITICAL, 30)
            """ """  """
            
            fhm.learnModel(inFiltered,inTraining,inField,inSplit,inSeed,outModel,outMatrix,inClassifier)
            self.iface.messageBar().pushMessage("Learning done with "+str(inClassifier)+": ", "Matrix confusion in" +str(outMatrix), level=QgsMessageBar.SUCCESS, duration=20)
                      
            pass
        
    def runClassify(self):
            """Run method that performs all the real work"""
    
            # show the dialog
            
            self.dlg.show()
            
            
            # Run the dialog event loop
            
            # See if OK was pressed
            result = self.dlg.exec_()
            if result:
                print 'result'  
                inFilteredStep3=self.dlg.inFilteredStep3.currentLayer()
                inFilteredStep3=inFilteredStep3.dataProvider().dataSourceUri()
                inMinSize=self.dlg.inMinSize.value()
                
                outRasterClass=self.dlg.outRasterClass.text()
                inModel=self.dlg.inModel.text()
                inFieldStep3=self.dlg.inFieldStep3.currentText()
                    
                
                """ DEBUG """
                #query=(str(inMinSize)+','+str(outRasterClass)+','+str(inModel))
                #self.iface.messageBar().pushMessage("Error", query, QgsMessageBar.CRITICAL, 30)
                """ DEBUG """
                #classifiedImage=fhm.classifyImage(inFilteredStep3,inTrainingStep3,outRasterClass,None,inMinSize,None,'Class',inNODATA=-10000)
                fhm.classifyImage(inFilteredStep3,inModel,outRasterClass,inMinSize,None,inFieldStep3,-10000)
                # Do something useful here - delete the line containing pass and
                # substitute with your code.
                self.iface.addRasterLayer(outRasterClass)
                self.iface.messageBar().pushMessage("New image : ",outRasterClass, level=QgsMessageBar.SUCCESS, duration=20)
                # Do something useful here - delete the line containing pass and
                # substitute with your code.
                pass
