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
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QSpacerItem, QStatusBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.actionLoadWf = QAction(MainWindow)
        self.actionLoadWf.setObjectName(u"actionLoadWf")
        self.actionSaveWf = QAction(MainWindow)
        self.actionSaveWf.setObjectName(u"actionSaveWf")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gbLayers = QGroupBox(self.centralwidget)
        self.gbLayers.setObjectName(u"gbLayers")
        self.horizontalLayout = QHBoxLayout(self.gbLayers)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lwWfLayers = QListWidget(self.gbLayers)
        self.lwWfLayers.setObjectName(u"lwWfLayers")

        self.horizontalLayout.addWidget(self.lwWfLayers)


        self.verticalLayout.addWidget(self.gbLayers)

        self.gbParams = QGroupBox(self.centralwidget)
        self.gbParams.setObjectName(u"gbParams")
        self.gridLayout = QGridLayout(self.gbParams)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lblDevice = QLabel(self.gbParams)
        self.lblDevice.setObjectName(u"lblDevice")

        self.gridLayout.addWidget(self.lblDevice, 0, 0, 1, 1)

        self.leWidth = QLineEdit(self.gbParams)
        self.leWidth.setObjectName(u"leWidth")

        self.gridLayout.addWidget(self.leWidth, 1, 2, 1, 1)

        self.comboDevice = QComboBox(self.gbParams)
        self.comboDevice.setObjectName(u"comboDevice")

        self.gridLayout.addWidget(self.comboDevice, 0, 2, 1, 1)

        self.lblWidth = QLabel(self.gbParams)
        self.lblWidth.setObjectName(u"lblWidth")

        self.gridLayout.addWidget(self.lblWidth, 1, 0, 1, 1)

        self.lblHeight = QLabel(self.gbParams)
        self.lblHeight.setObjectName(u"lblHeight")

        self.gridLayout.addWidget(self.lblHeight, 2, 0, 1, 1)

        self.leHeight = QLineEdit(self.gbParams)
        self.leHeight.setObjectName(u"leHeight")

        self.gridLayout.addWidget(self.leHeight, 2, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 1, 1, 1)


        self.verticalLayout.addWidget(self.gbParams)


        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.view = QGraphicsView(self.centralwidget)
        self.view.setObjectName(u"view")

        self.horizontalLayout_2.addWidget(self.view)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionLoadWf)
        self.menuFile.addAction(self.actionSaveWf)
        self.menuFile.addAction(self.actionExit)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"SMA smart watch face creator", None))
        self.actionLoadWf.setText(QCoreApplication.translate("MainWindow", u"Load Watch Face", None))
        self.actionSaveWf.setText(QCoreApplication.translate("MainWindow", u"Save Watch Face", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.gbLayers.setTitle(QCoreApplication.translate("MainWindow", u"Layers", None))
        self.gbParams.setTitle(QCoreApplication.translate("MainWindow", u"Parameters", None))
        self.lblDevice.setText(QCoreApplication.translate("MainWindow", u"Device", None))
        self.lblWidth.setText(QCoreApplication.translate("MainWindow", u"Width", None))
        self.lblHeight.setText(QCoreApplication.translate("MainWindow", u"Height", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi

