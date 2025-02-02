# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'wf_creator.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGraphicsView, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QStatusBar, QVBoxLayout, QWidget)
import wf_creator_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(860, 600)
        icon = QIcon()
        icon.addFile(u":/icon/resources/icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.actionLoadWf = QAction(MainWindow)
        self.actionLoadWf.setObjectName(u"actionLoadWf")
        self.actionSaveWf = QAction(MainWindow)
        self.actionSaveWf.setObjectName(u"actionSaveWf")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionExport_Preview = QAction(MainWindow)
        self.actionExport_Preview.setObjectName(u"actionExport_Preview")
        self.actionPreview = QAction(MainWindow)
        self.actionPreview.setObjectName(u"actionPreview")
        self.actionSaveImages = QAction(MainWindow)
        self.actionSaveImages.setObjectName(u"actionSaveImages")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gbLayers = QGroupBox(self.centralwidget)
        self.gbLayers.setObjectName(u"gbLayers")
        self.verticalLayout_2 = QVBoxLayout(self.gbLayers)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lwWfLayers = QListWidget(self.gbLayers)
        self.lwWfLayers.setObjectName(u"lwWfLayers")

        self.verticalLayout_2.addWidget(self.lwWfLayers)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btnAddLayer = QPushButton(self.gbLayers)
        self.btnAddLayer.setObjectName(u"btnAddLayer")

        self.horizontalLayout.addWidget(self.btnAddLayer)

        self.btnRemoveLayer = QPushButton(self.gbLayers)
        self.btnRemoveLayer.setObjectName(u"btnRemoveLayer")

        self.horizontalLayout.addWidget(self.btnRemoveLayer)

        self.btnRemoveAllLayers = QPushButton(self.gbLayers)
        self.btnRemoveAllLayers.setObjectName(u"btnRemoveAllLayers")

        self.horizontalLayout.addWidget(self.btnRemoveAllLayers)

        self.btnMoveLayerUp = QPushButton(self.gbLayers)
        self.btnMoveLayerUp.setObjectName(u"btnMoveLayerUp")
        self.btnMoveLayerUp.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.btnMoveLayerUp)

        self.btnMoveLayerDown = QPushButton(self.gbLayers)
        self.btnMoveLayerDown.setObjectName(u"btnMoveLayerDown")
        self.btnMoveLayerDown.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.btnMoveLayerDown)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout.addWidget(self.gbLayers)

        self.gbParams = QGroupBox(self.centralwidget)
        self.gbParams.setObjectName(u"gbParams")
        self.gridLayout = QGridLayout(self.gbParams)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lblDevice = QLabel(self.gbParams)
        self.lblDevice.setObjectName(u"lblDevice")

        self.gridLayout.addWidget(self.lblDevice, 0, 0, 1, 1)

        self.comboDevice = QComboBox(self.gbParams)
        self.comboDevice.setObjectName(u"comboDevice")

        self.gridLayout.addWidget(self.comboDevice, 0, 2, 1, 1)

        self.lblWidth = QLabel(self.gbParams)
        self.lblWidth.setObjectName(u"lblWidth")

        self.gridLayout.addWidget(self.lblWidth, 1, 0, 1, 1)

        self.lblHeight = QLabel(self.gbParams)
        self.lblHeight.setObjectName(u"lblHeight")

        self.gridLayout.addWidget(self.lblHeight, 2, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 1, 1, 1)

        self.spinboxWidth = QSpinBox(self.gbParams)
        self.spinboxWidth.setObjectName(u"spinboxWidth")
        self.spinboxWidth.setMinimum(100)
        self.spinboxWidth.setMaximum(700)

        self.gridLayout.addWidget(self.spinboxWidth, 1, 2, 1, 1)

        self.spinboxHeight = QSpinBox(self.gbParams)
        self.spinboxHeight.setObjectName(u"spinboxHeight")
        self.spinboxHeight.setMinimum(100)
        self.spinboxHeight.setMaximum(700)

        self.gridLayout.addWidget(self.spinboxHeight, 2, 2, 1, 1)


        self.verticalLayout.addWidget(self.gbParams)


        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.view = QGraphicsView(self.centralwidget)
        self.view.setObjectName(u"view")

        self.horizontalLayout_2.addWidget(self.view)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 860, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName(u"menuTools")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menuFile.addAction(self.actionLoadWf)
        self.menuFile.addAction(self.actionSaveWf)
        self.menuFile.addAction(self.actionExit)
        self.menuTools.addAction(self.actionPreview)
        self.menuTools.addAction(self.actionSaveImages)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"SMA smart watch face creator", None))
        self.actionLoadWf.setText(QCoreApplication.translate("MainWindow", u"Load Watch Face", None))
        self.actionSaveWf.setText(QCoreApplication.translate("MainWindow", u"Save Watch Face", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionExport_Preview.setText(QCoreApplication.translate("MainWindow", u"Export Preview", None))
        self.actionPreview.setText(QCoreApplication.translate("MainWindow", u"Create Preview", None))
        self.actionSaveImages.setText(QCoreApplication.translate("MainWindow", u"Save all images", None))
        self.gbLayers.setTitle(QCoreApplication.translate("MainWindow", u"Layers", None))
        self.btnAddLayer.setText(QCoreApplication.translate("MainWindow", u"+ Add", None))
        self.btnRemoveLayer.setText(QCoreApplication.translate("MainWindow", u"- Remove", None))
        self.btnRemoveAllLayers.setText(QCoreApplication.translate("MainWindow", u"Remove All", None))
        self.btnMoveLayerUp.setText(QCoreApplication.translate("MainWindow", u"Up", None))
        self.btnMoveLayerDown.setText(QCoreApplication.translate("MainWindow", u"Down", None))
        self.gbParams.setTitle(QCoreApplication.translate("MainWindow", u"Parameters", None))
        self.lblDevice.setText(QCoreApplication.translate("MainWindow", u"Device", None))
        self.lblWidth.setText(QCoreApplication.translate("MainWindow", u"Width", None))
        self.lblHeight.setText(QCoreApplication.translate("MainWindow", u"Height", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuTools.setTitle(QCoreApplication.translate("MainWindow", u"Tools", None))
    # retranslateUi

