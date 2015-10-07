# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Flaechensumme
                                 A QGIS plugin
 Berechnet Flächensummen
                              -------------------
        begin                : 2015-09-25
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Max G.
        email                : Lorjax@gmx.de
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
from PyQt4.QtGui import QAction, QIcon, QTableWidgetItem
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from flaechen_summe_dialog import FlaechensummeDialog
import os.path
import processing
from qgis.core import QgsFeatureRequest


class Flaechensumme:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Flaechensumme_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = FlaechensummeDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Flächensumme')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Flaechensumme')
        self.toolbar.setObjectName(u'Flaechensumme')

        self.layers = self.iface.legendInterface().layers()
        self.vLayers = self.initVectorLayers()

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
        return QCoreApplication.translate('Flaechensumme', message)


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

        #icon = QIcon(icon_path)
        icon = QIcon(':/plugins/Flaechensumme/icon.png')
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Flaechensumme/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Flächensummen...'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.initComboBox()
        self.initAttributeSelect()
        self.initTable()
        self.dlg.comboBox.currentIndexChanged.connect(self.currentLayerChanged)
        self.dlg.attributeSelect.currentIndexChanged.connect(self.currentClassificationChanged)
       


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Flächensumme'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        self.layers = self.iface.legendInterface().layers()
        self.vLayers = self.initVectorLayers()

        self.initComboBox()
        self.initAttributeSelect()
        self.initTable()
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
            
    def initTable(self):
        """Initializes a tablewidget-item in order to display the results"""
        self.dlg.tableWidget.clear()
        self.dlg.tableWidget.setRowCount(6)
        self.dlg.tableWidget.setColumnCount(6)

        self.dlg.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem("Jahr"))
        self.dlg.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem("Fläche [ha]".decode('utf8')))
        self.dlg.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem("kleinste Fläche [ha]".decode('utf8')))
        self.dlg.tableWidget.setHorizontalHeaderItem(3, QTableWidgetItem("größte Fläche [ha]".decode('utf8')))
        self.dlg.tableWidget.setHorizontalHeaderItem(4, QTableWidgetItem("durchschnittl. Fläche [ha]".decode('utf8')))
        self.dlg.tableWidget.setHorizontalHeaderItem(5, QTableWidgetItem("Anzahl bearbeiteter Flächen".decode('utf8')))


    def initComboBox(self):
        """Inserts all available vectorlayers in the comboBox"""
        # Test, if there are any vector layers available
        self.dlg.comboBox.clear()
        if len(self.vLayers) > 0:
            self.dlg.comboBox.setEnabled(True)
            self.dlg.attributeSelect.setEnabled(True)
            layer_names = []
            for layer in self.vLayers:
                layer_names.append(layer.name())
            self.dlg.comboBox.addItems(layer_names) # vectorlayers available, set combobox content
        else:
            self.dlg.comboBox.addItem("keine geeigneten Layer vorhanden!") # no vectorlayer, set user-warning
            self.dlg.comboBox.setEnabled(False) # disable combobox
            self.dlg.attributeSelect.setEnabled(False) # disable classification selector
            

    def initAttributeSelect(self):
        """Inserts all attributes of the selected Layer into the combobox"""
        self.dlg.attributeSelect.clear()
        if len(self.vLayers) > 0:
            currentLayer = self.vLayers[self.dlg.comboBox.currentIndex()]
            currentLayerFieldNames = []
            for field in currentLayer.pendingFields():
                currentLayerFieldNames.append(field.name())
            self.dlg.attributeSelect.addItems(currentLayerFieldNames)

    def initVectorLayers(self):
        """Returns all vectorlayers"""
        try:
            layer_list = []
            for layer in self.layers:
                if layer.type() == 0: # check if current Layer is a vectorlayer
                    layer_list.append(layer) # if so, add it to the array
            return layer_list
        except:
            print 'Error!'

    def currentLayerChanged(self):
        """Triggered by the "currentIndexChanged"-event of the layer combobox"""
        self.dlg.attributeSelect.clear()
        self.initAttributeSelect()

    def calculateArea(self):
        currentLayer = self.vLayers[self.dlg.comboBox.currentIndex()]
        area = 0
        for f in currentLayer.getFeatures():
            area += f.geometry().area()
        return area /100 /100 #in ha

    def currentClassificationChanged(self):
        """Handler for changing the classification. Includes calculation of the desired results."""
        try:
            # Reading current layer and classification out of the comboboxes
            currentLayer = self.vLayers[self.dlg.comboBox.currentIndex()]
            currentClassification = self.dlg.attributeSelect.currentText()

            # clear table widet and initializing it again
            self.dlg.tableWidget.clear()
            self.initTable()

        
            # saving possible classifications in a set -> Set contains only unique classifications
            allClassifications = set()
            for feature in currentLayer.getFeatures():
                allClassifications.add(feature[currentClassification])

            # setting row count
            self.dlg.tableWidget.setRowCount(len(allClassifications))

            # iterator for rows
            rowCount = 0

            # initialising filter expression
            for classification in allClassifications:
                request = QgsFeatureRequest()
                request.setFilterExpression(str(currentClassification) + ' = ' + str(classification))

                # helper values for storing results
                area_total = 0
                area_collection = []

                for feature in currentLayer.getFeatures(request):
                    print str(currentClassification) + ' = ' + str(classification) + " --- " + str(feature.geometry().area())
                    area_total += feature.geometry().area()
                    area_collection.append(feature.geometry().area())


                # write out the results
                self.dlg.tableWidget.setItem(rowCount, 0, QTableWidgetItem(str(classification)))
                self.dlg.tableWidget.setItem(rowCount, 1, QTableWidgetItem(str(round(area_total / 10000, 2))))
                self.dlg.tableWidget.setItem(rowCount, 2, QTableWidgetItem(str(round(min(area_collection) / 10000, 2))))
                self.dlg.tableWidget.setItem(rowCount, 3, QTableWidgetItem(str(round(max(area_collection) / 10000, 2))))
                self.dlg.tableWidget.setItem(rowCount, 4, QTableWidgetItem(str(round(sum(area_collection) / len(area_collection) / 10000,2))))
                self.dlg.tableWidget.setItem(rowCount, 5, QTableWidgetItem(str(len(area_collection))))
                rowCount += 1
        except:
            print 'Error!'


        # Source: http://docs.qgis.org/2.2/de/docs/user_manual/processing/console.html
        # and http://docs.qgis.org/2.8/en/docs/user_manual/processing_algs/qgis/vector_table_tools.html#basic-statistics-for-numeric-fields
        # i = 1            
        # for e in allClassifications:
        #     results = processing.runalg('qgis:basicstatisticsfornumericfields', currentLayer, currentClassification, 'a')
        #     self.dlg.tableWidget.setItem(i, 1, QTableWidgetItem(str(e)))
        #     self.dlg.tableWidget.setItem(i, 2, QTableWidgetItem(str(results['SUM'])))
        #     self.dlg.tableWidget.setItem(i, 3, QTableWidgetItem(str(results['MIN'])))
        #     self.dlg.tableWidget.setItem(i, 4, QTableWidgetItem(str(results['MAX'])))
        #     self.dlg.tableWidget.setItem(i, 5, QTableWidgetItem(str(results['MEAN'])))
        #     self.dlg.tableWidget.setItem(i, 6, QTableWidgetItem(str(results['COUNT'])))
        #     i += 1
