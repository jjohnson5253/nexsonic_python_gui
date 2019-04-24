#!/usr/bin/env python
#
# Jake Johnson
# 4/21/19
# 
# To run this on windows 10 with python3:
#
# 1. open command prompt
#
# 2. create virtual environment by typing:
#           py -m venv venv
#    or if you have already done this, there should be a directory "venv\"
#
# 3. start virtual environment by running: 
#           call venv\Script\activate.bat
#
# If PyWt is not installed, run:
#           pip install PyQt5==5.9.2
#
# Refer to this site for above instructions and more:
#       https://build-system.fman.io/pyqt5-tutorial
#

from PyQt5.QtCore import QDateTime, Qt, QTimer, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)
import serial

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        # freq, dac, duty labels
        self.freqLabel = QLabel('')
        self.dacLabel = QLabel('')
        self.dutyLabel = QLabel('')

        # calculated labels
        self.iadcLabel = QLabel('')
        self.vadcLabel = QLabel('')
        self.voltLabel = QLabel('')
        self.currLabel = QLabel('')
        self.powLabel = QLabel('')
        self.impLabel = QLabel('')

        self.originalPalette = QApplication.palette()

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)

        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)

        disableWidgetsCheckBox = QCheckBox("&Disable widgets")

        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLeftGroupBox()
        self.createADCReadingBox()
        self.createProgressBar()

        styleComboBox.activated[str].connect(self.changeStyle)
        self.useStylePaletteCheckBox.toggled.connect(self.changePalette)
        disableWidgetsCheckBox.toggled.connect(self.topLeftGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.topRightGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.bottomLeftGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.ADCReadingBox.setDisabled)

        topLayout = QHBoxLayout()
        topLayout.addWidget(styleLabel)
        topLayout.addWidget(styleComboBox)
        topLayout.addStretch(1)
        # topLayout.addWidget(self.useStylePaletteCheckBox)
        # topLayout.addWidget(disableWidgetsCheckBox)

        ## tabs

        tabWidget = QTabWidget()

        # settings boxes height
        self.topLeftGroupBox.setFixedHeight(150)
        self.topRightGroupBox.setFixedHeight(150)
        self.bottomLeftGroupBox.setFixedHeight(150)
        self.topLeftGroupBox.setFixedWidth(300)
        self.topRightGroupBox.setFixedWidth(300)
        self.bottomLeftGroupBox.setFixedWidth(300)

        # settings tab
        settingsTab = QWidget()
        settingsMainLayout = QVBoxLayout()
        settingsGrid = QGridLayout()
        updateSettingsValsButton = QPushButton('Update Values')
        updateSettingsValsButton.clicked.connect(self.updateSettingsVals)
        updateSettingsValsButton.setFixedWidth(100)
        settingsMainLayout.addWidget(updateSettingsValsButton)
        settingsGrid.addWidget(self.topLeftGroupBox, 1, 0)
        settingsGrid.addWidget(self.topRightGroupBox, 1, 1)
        settingsGrid.addWidget(self.bottomLeftGroupBox, 2, 0)
        settingsMainLayout.addLayout(settingsGrid)
        settingsTab.setLayout(settingsMainLayout)

        # main tab
        mainTab = QWidget()
        mainvbox = QVBoxLayout()
        mainvbox.addWidget(self.ADCReadingBox)
        mainTab.setFixedHeight(140)
        mainTab.setLayout(mainvbox)

        # add tabs to tab widget
        tabWidget.addTab(settingsTab, 'Settings')
        tabWidget.addTab(mainTab, 'Main')

        ## main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(tabWidget)

        # set main layout
        self.setLayout(mainLayout)

        # set window title
        self.setWindowTitle("Nexsonic UTDS")

        # set style
        self.changeStyle('Windows')

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) / 100)

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Frequency (Hz)")

        # buttons
        incButton = QPushButton('Increase', self)
        decButton = QPushButton('Decrease', self)
        incButton.clicked.connect(self.incFreq)
        decButton.clicked.connect(self.decFreq)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(incButton)
        layout.addWidget(decButton)
        layout.addWidget(QLabel('Frequency (Hz):'))
        layout.addWidget(self.freqLabel)
        # layout.addStretch(1)
        self.topLeftGroupBox.setLayout(layout)    

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("Duty Cycle")

        # buttons
        incButton = QPushButton('Increase', self)
        decButton = QPushButton('Decrease', self)
        incButton.clicked.connect(self.incDuty)
        decButton.clicked.connect(self.decDuty)

        layout = QVBoxLayout()
        layout.addWidget(incButton)
        layout.addWidget(decButton)
        layout.addWidget(QLabel('Duty Cycle (%):'))
        layout.addWidget(self.dutyLabel)
        # layout.addStretch(1) 
        self.topRightGroupBox.setLayout(layout)

    def createBottomLeftGroupBox(self):
        self.bottomLeftGroupBox = QGroupBox("DAC")

        # buttons
        incButton = QPushButton('Increase', self)
        decButton = QPushButton('Decrease', self)
        incButton.clicked.connect(self.incDac)
        decButton.clicked.connect(self.decDac)

        layout = QVBoxLayout()
        layout.addWidget(incButton)
        layout.addWidget(decButton)
        layout.addWidget(QLabel('DAC (mv):'))
        layout.addWidget(self.dacLabel)
        layout.addWidget
        # layout.addStretch(1) 
        self.bottomLeftGroupBox.setLayout(layout)

    def createADCReadingBox(self):
        self.ADCReadingBox = QGroupBox("Readings")

        # buttons
        calcButton = QPushButton('Read ADC', self)

        layout = QVBoxLayout()
        layout.addWidget(calcButton)
        calcButton.clicked.connect(self.getADCReading)

        readingsLayout = QHBoxLayout()

        vadcLabelLayout = QVBoxLayout()
        vadcLabelLayout.addWidget(QLabel('Raw Voltage ADC:'))
        vadcLabelLayout.addWidget(self.vadcLabel)

        iadcLabelLayout = QVBoxLayout()
        iadcLabelLayout.addWidget(QLabel('Raw Current ADC:'))
        iadcLabelLayout.addWidget(self.iadcLabel)

        voltLabelLayout = QVBoxLayout()
        voltLabelLayout.addWidget(QLabel('Voltage (mV):'))
        voltLabelLayout.addWidget(self.voltLabel)

        currLabelLayout = QVBoxLayout()
        currLabelLayout.addWidget(QLabel('Current (mA):'))
        currLabelLayout.addWidget(self.currLabel)

        powLabelLayout = QVBoxLayout()
        powLabelLayout.addWidget(QLabel('Power (mW):'))
        powLabelLayout.addWidget(self.powLabel)

        impLabelLayout = QVBoxLayout()
        impLabelLayout.addWidget(QLabel('Impedance (Ohms):'))
        impLabelLayout.addWidget(self.impLabel)

        readingsLayout.addLayout(vadcLabelLayout)
        readingsLayout.addLayout(iadcLabelLayout)
        readingsLayout.addLayout(voltLabelLayout)
        readingsLayout.addLayout(currLabelLayout)
        readingsLayout.addLayout(powLabelLayout)
        readingsLayout.addLayout(impLabelLayout)

        layout.addLayout(readingsLayout)
        # layout.addStretch(1) 
        self.ADCReadingBox.setLayout(layout)

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)

    @pyqtSlot()
    def decDuty(self):
        print("decrease")
        ser = serial.Serial('COM14')
        ser.write(b'1')  # 1 = duty change
        ser.write(b'2') # 2 = decrease duty
        self.dutyLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def incDuty(self):
        print("increase")
        ser = serial.Serial('COM14')
        ser.write(b'1')  # 1 = duty change
        ser.write(b'1') # 1 = increase duty
        self.dutyLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def decFreq(self):
        print("decrease")
        ser = serial.Serial('COM14')
        ser.write(b'2')  # 2 = freq change
        ser.write(b'1') # 1 = decrease freq
        self.freqLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def incFreq(self):
        print("increase")
        ser = serial.Serial('COM14')
        ser.write(b'2')  # 2 = freq change
        ser.write(b'2') # 2 = increase freq
        self.freqLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def decDac(self):
        print("decrease")
        ser = serial.Serial('COM14')
        ser.write(b'3')  # 2 = freq change
        ser.write(b'1') # 1 = decrease freq
        self.dacLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def incDac(self):
        print("increase")
        ser = serial.Serial('COM14')
        ser.write(b'3')  # 3 = dac change
        ser.write(b'2') # 2 = increase dac
        self.dacLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def getADCReading(self):
        print("reading adc")
        ser = serial.Serial('COM14')
        ser.write(b'5')  # 5 = read adcs
        self.vadcLabel.setText(ser.readline().decode("utf-8"))
        self.iadcLabel.setText(ser.readline().decode("utf-8"))
        self.voltLabel.setText(ser.readline().decode("utf-8"))
        self.currLabel.setText(ser.readline().decode("utf-8"))
        self.impLabel.setText(ser.readline().decode("utf-8"))
        self.powLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def updateSettingsVals(self):
        print("updating settings values")
        ser = serial.Serial('COM14')
        ser.write(b'6')  # 5 = read adcs
        self.freqLabel.setText(ser.readline().decode("utf-8"))
        self.dutyLabel.setText(ser.readline().decode("utf-8"))
        self.dacLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

if __name__ == '__main__':

    import sys
    import serial

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()

    sys.exit(app.exec_()) 

    ser.close()