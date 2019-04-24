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
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)
import serial
import time

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

        # sweep table
        self.sweepTable = QTableWidget()

        self.originalPalette = QApplication.palette()

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)

        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)

        disableWidgetsCheckBox = QCheckBox("&Disable widgets")

        self.createFrequencyGroupBox()
        # self.createDutyCycleGroupBox()
        self.createDacGroupBox()
        self.createAdcGroupBox()
        self.createSweepGroupBox()
        self.createProgressBar()

        styleComboBox.activated[str].connect(self.changeStyle)
        self.useStylePaletteCheckBox.toggled.connect(self.changePalette)
        disableWidgetsCheckBox.toggled.connect(self.frequencyGroupBox.setDisabled)
        # disableWidgetsCheckBox.toggled.connect(self.dutyCycleGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.dacGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.adcGroupBox.setDisabled)

        topLayout = QHBoxLayout()
        topLayout.addWidget(styleLabel)
        topLayout.addWidget(styleComboBox)
        topLayout.addStretch(1)
        # topLayout.addWidget(self.useStylePaletteCheckBox)
        # topLayout.addWidget(disableWidgetsCheckBox)

        ## tabs

        tabWidget = QTabWidget()

        # settings boxes height
        self.frequencyGroupBox.setFixedHeight(160)
        # self.dutyCycleGroupBox.setFixedHeight(140)
        self.dacGroupBox.setFixedHeight(160)
        self.adcGroupBox.setFixedHeight(326)
        self.frequencyGroupBox.setFixedWidth(200)
        # self.dutyCycleGroupBox.setFixedWidth(300)
        self.dacGroupBox.setFixedWidth(200)
        self.adcGroupBox.setFixedWidth(200)

        # main settings layout
        mainSettingsVLayout = QVBoxLayout()
        # add button on top
        updateSettingsValsButton = QPushButton('Update Values')
        updateSettingsValsButton.clicked.connect(self.updateSettingsVals)
        updateSettingsValsButton.setFixedWidth(100)
        mainSettingsVLayout.addWidget(updateSettingsValsButton)
        # create vertical layout for freq,duty,dac boxes
        freqDutyDacVLayout = QVBoxLayout()
        freqDutyDacVLayout.addWidget(self.frequencyGroupBox)
        # freqDutyDacVLayout.addWidget(self.dutyCycleGroupBox)
        freqDutyDacVLayout.addWidget(self.dacGroupBox)
        # create horizontal layout
        freqDutyDacAdcHLayout = QHBoxLayout()
        # add freq,duty,dac box layout to horizontal layout
        freqDutyDacAdcHLayout.addLayout(freqDutyDacVLayout)
        # add adc box to horizontal layout
        freqDutyDacAdcHLayout.addWidget(self.adcGroupBox)
        # add horizontal layout to main vertical layout
        mainSettingsVLayout.addLayout(freqDutyDacAdcHLayout)

        # settings tab
        settingsTab = QWidget()

        # set settings tab layout to main vertical layout
        settingsTab.setLayout(mainSettingsVLayout)

        # sweep tab
        sweepTab = QWidget()
        sweepvbox = QVBoxLayout()
        sweepvbox.addWidget(self.sweepGroupBox)
        sweepTab.setLayout(sweepvbox)

        # add tabs to tab widget
        tabWidget.addTab(settingsTab, 'Settings')
        tabWidget.addTab(sweepTab, 'Sweep')

        # when tab changed action
        tabWidget.currentChanged.connect(self.onChange) #changed!

        ## main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(tabWidget)

        # set main layout
        self.setLayout(mainLayout)

        # set window title
        self.setWindowTitle("Nexsonic UTDS")

        # set style
        self.changeStyle('WindowsVista')

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

    def createFrequencyGroupBox(self):
        self.frequencyGroupBox = QGroupBox("Frequency")

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
        self.frequencyGroupBox.setLayout(layout)    

    # def createDutyCycleGroupBox(self):
    #     self.dutyCycleGroupBox = QGroupBox("Duty Cycle")

    #     # buttons
    #     incButton = QPushButton('Increase', self)
    #     decButton = QPushButton('Decrease', self)
    #     incButton.clicked.connect(self.incDuty)
    #     decButton.clicked.connect(self.decDuty)

    #     layout = QVBoxLayout()
    #     layout.addWidget(incButton)
    #     layout.addWidget(decButton)
    #     layout.addWidget(QLabel('Duty Cycle (%):'))
    #     layout.addWidget(self.dutyLabel)
    #     # layout.addStretch(1) 
    #     self.dutyCycleGroupBox.setLayout(layout)

    def createDacGroupBox(self):
        self.dacGroupBox = QGroupBox("DAC")

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
        self.dacGroupBox.setLayout(layout)

    def createAdcGroupBox(self):
        self.adcGroupBox = QGroupBox("ADC")

        # buttons
        # calcButton = QPushButton('Read ADC', self)

        layout = QVBoxLayout()
        # layout.addWidget(calcButton)
        # calcButton.clicked.connect(self.getADCReading)

        readingsLayout = QVBoxLayout()

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
        powLabelLayout.addWidget(QLabel('Power (W):'))
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
        self.adcGroupBox.setLayout(layout)

    def createSweepGroupBox(self):
        self.sweepGroupBox = QGroupBox("")

        # create vertical layout
        layout = QVBoxLayout()

        # readingsWidget = QtWidgets()
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
        powLabelLayout.addWidget(QLabel('Power (W):'))
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

        # readingsWidget.addLayout(readingsLayout)

        # setup table
        self.sweepTable.setRowCount(71);
        self.sweepTable.setColumnCount(7)
        self.sweepTable.setItem(0,0, QTableWidgetItem("Freq (Hz)"))
        self.sweepTable.setItem(0,1, QTableWidgetItem("Voltage ADC"))
        self.sweepTable.setItem(0,2, QTableWidgetItem("Current ADC"))
        self.sweepTable.setItem(0,3, QTableWidgetItem("Voltage (mV)"))
        self.sweepTable.setItem(0,4, QTableWidgetItem("Current (mA)"))
        self.sweepTable.setItem(0,5, QTableWidgetItem("Z (Ohms)"))
        self.sweepTable.setItem(0,6, QTableWidgetItem("Power (W)"))

        # buttons
        sweepButton = QPushButton('Sweep', self)
        sweepButton.setFixedWidth(100)
        sweepButton.clicked.connect(self.readSweep)

        # add button and table
        layout.addWidget(sweepButton)
        # layout.addLayout(readingsLayout)
        layout.addWidget(QLabel('Table of readings:'))
        layout.addWidget(self.sweepTable)

        # set box layout
        self.sweepGroupBox.setLayout(layout)

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)

    # @pyqtSlot()
    # def decDuty(self):
    #     print("decrease")
    #     ser = serial.Serial('COM14')
    #     ser.write(b'1')  # 1 = duty change
    #     ser.write(b'2') # 2 = decrease duty
    #     self.dutyLabel.setText(ser.readline().decode("utf-8"))
    #     ser.close()

    # @pyqtSlot()
    # def incDuty(self):
    #     print("increase")
    #     ser = serial.Serial('COM14')
    #     ser.write(b'1')  # 1 = duty change
    #     ser.write(b'1') # 1 = increase duty
    #     self.dutyLabel.setText(ser.readline().decode("utf-8"))
    #     ser.close()

    @pyqtSlot()
    def decFreq(self):
        print("decrease")
        ser = serial.Serial('COM14')
        ser.write(b'2')  # 2 = freq change
        ser.write(b'1') # 1 = decrease freq
        self.freqLabel.setText(ser.readline().decode("utf-8"))
        # receive adc data as well
        self.vadcLabel.setText(ser.readline().decode("utf-8"))
        self.iadcLabel.setText(ser.readline().decode("utf-8"))
        self.voltLabel.setText(ser.readline().decode("utf-8"))
        self.currLabel.setText(ser.readline().decode("utf-8"))
        self.impLabel.setText(ser.readline().decode("utf-8"))
        self.powLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def incFreq(self):
        print("increase")
        ser = serial.Serial('COM14')
        ser.write(b'2')  # 2 = freq change
        ser.write(b'2') # 2 = increase freq
        self.freqLabel.setText(ser.readline().decode("utf-8"))
        # receive adc data as well
        self.vadcLabel.setText(ser.readline().decode("utf-8"))
        self.iadcLabel.setText(ser.readline().decode("utf-8"))
        self.voltLabel.setText(ser.readline().decode("utf-8"))
        self.currLabel.setText(ser.readline().decode("utf-8"))
        self.impLabel.setText(ser.readline().decode("utf-8"))
        self.powLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def decDac(self):
        print("decrease")
        ser = serial.Serial('COM14')
        ser.write(b'3')  # 2 = freq change
        ser.write(b'1') # 1 = decrease freq
        self.dacLabel.setText(ser.readline().decode("utf-8"))
        # receive adc data as well
        self.vadcLabel.setText(ser.readline().decode("utf-8"))
        self.iadcLabel.setText(ser.readline().decode("utf-8"))
        self.voltLabel.setText(ser.readline().decode("utf-8"))
        self.currLabel.setText(ser.readline().decode("utf-8"))
        self.impLabel.setText(ser.readline().decode("utf-8"))
        self.powLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def incDac(self):
        print("increase")
        ser = serial.Serial('COM14')
        ser.write(b'3')  # 3 = dac change
        ser.write(b'2') # 2 = increase dac
        self.dacLabel.setText(ser.readline().decode("utf-8"))
        # receive adc data as well
        self.vadcLabel.setText(ser.readline().decode("utf-8"))
        self.iadcLabel.setText(ser.readline().decode("utf-8"))
        self.voltLabel.setText(ser.readline().decode("utf-8"))
        self.currLabel.setText(ser.readline().decode("utf-8"))
        self.impLabel.setText(ser.readline().decode("utf-8"))
        self.powLabel.setText(ser.readline().decode("utf-8"))
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
        ser.write(b'6')  # 6 = update settings vals
        self.freqLabel.setText(ser.readline().decode("utf-8"))
        self.dutyLabel.setText(ser.readline().decode("utf-8"))
        self.dacLabel.setText(ser.readline().decode("utf-8"))
        # receive adc data as well
        self.vadcLabel.setText(ser.readline().decode("utf-8"))
        self.iadcLabel.setText(ser.readline().decode("utf-8"))
        self.voltLabel.setText(ser.readline().decode("utf-8"))
        self.currLabel.setText(ser.readline().decode("utf-8"))
        self.impLabel.setText(ser.readline().decode("utf-8"))
        self.powLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def readSweep(self):
        print("reading sweep")
        ser = serial.Serial('COM14')

        ser.write(b'4')  # 4 = sweep

        rowCnt = 1
        colCnt = 0

        # if(ser.readline().decode("utf-8") != "ENDSWP"):
        for i in range(70):

            # set freq
            self.sweepTable.setItem(rowCnt,colCnt, QTableWidgetItem(ser.readline().decode("utf-8")))
            # increase column count to write into next column
            colCnt = colCnt + 1

            # set vadc
            # For some reason, I can a character from sci char array sent before this, 
            # so have to splice
            vadcStr = ser.readline().decode("utf-8")
            vadcStr = vadcStr[2:7]
            self.sweepTable.setItem(rowCnt,colCnt, QTableWidgetItem(vadcStr))
            self.vadcLabel.setText(vadcStr)
            # increase column count to write into next column
            colCnt = colCnt + 1

            # set iadc
            iadc = ser.readline().decode("utf-8")
            self.sweepTable.setItem(rowCnt,colCnt, QTableWidgetItem(iadc))
            self.iadcLabel.setText(iadc)
            # increase column count to write into next column
            colCnt = colCnt + 1

            # set voltage
            volts = ser.readline().decode("utf-8")
            self.sweepTable.setItem(rowCnt,colCnt, QTableWidgetItem(volts))
            self.voltLabel.setText(volts)
            # increase column count to write into next column
            colCnt = colCnt + 1

            # set current
            curr = ser.readline().decode("utf-8")
            self.sweepTable.setItem(rowCnt,colCnt, QTableWidgetItem(curr))
            self.currLabel.setText(curr)
            # increase column count to write into next column
            colCnt = colCnt + 1

            # set impedance
            imp = ser.readline().decode("utf-8")
            self.sweepTable.setItem(rowCnt,colCnt, QTableWidgetItem(imp))
            self.impLabel.setText(imp)
            # increase column count to write into next column
            colCnt = colCnt + 1

            # set power
            power = ser.readline().decode("utf-8")
            self.sweepTable.setItem(rowCnt,colCnt, QTableWidgetItem(power))
            self.powLabel.setText(power)
            # increase column count to write into next column
            colCnt = colCnt + 1

            # reset column to write back to column 0
            colCnt = 0
            # increment rowCnt to write into next row
            rowCnt = rowCnt + 1

            app.processEvents()

        ser.close()

    # https://stackoverflow.com/questions/21562485/pyqt-qtabwidget-currentchanged
    @pyqtSlot()  
    def onChange(self): #changed!
        print("tab changed")
        # reset labels
        self.vadcLabel.setText('')
        self.iadcLabel.setText('')
        self.voltLabel.setText('')
        self.currLabel.setText('')
        self.impLabel.setText('')
        self.powLabel.setText('')
        self.freqLabel.setText('')
        self.dutyLabel.setText('')
        self.dacLabel.setText('')

if __name__ == '__main__':

    import sys
    import serial

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()

    sys.exit(app.exec_()) 

    ser.close()