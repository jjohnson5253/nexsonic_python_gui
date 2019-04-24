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

        self.left = 1000
        self.top = 1000

        # freq label
        self.freqLabel = QLabel('56000' + ' Hz')
        self.dacLabel = QLabel('160' + ' mV')
        self.dutyLabel = QLabel('50' + '%')


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
        self.createBottomRightGroupBox()
        self.createProgressBar()

        styleComboBox.activated[str].connect(self.changeStyle)
        self.useStylePaletteCheckBox.toggled.connect(self.changePalette)
        disableWidgetsCheckBox.toggled.connect(self.topLeftGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.topRightGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.bottomLeftGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.bottomRightGroupBox.setDisabled)

        topLayout = QHBoxLayout()
        topLayout.addWidget(styleLabel)
        topLayout.addWidget(styleComboBox)
        topLayout.addStretch(1)
        # topLayout.addWidget(self.useStylePaletteCheckBox)
        # topLayout.addWidget(disableWidgetsCheckBox)

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.addWidget(self.bottomLeftGroupBox, 2, 0)
        # mainLayout.addWidget(self.bottomRightGroupBox, 2, 1)
        mainLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Styles")
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
        self.topLeftGroupBox = QGroupBox("Frequency")

        # buttons
        incButton = QPushButton('Increase', self)
        decButton = QPushButton('Decrease', self)
        incButton.clicked.connect(self.incFreq)
        decButton.clicked.connect(self.decFreq)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(incButton)
        layout.addWidget(decButton)
        layout.addWidget(QLabel('Frequency:'))
        layout.addWidget(self.freqLabel)
        layout.addStretch(1)
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
        layout.addWidget(QLabel('Duty Cycle:'))
        layout.addWidget(self.dutyLabel)
        layout.addStretch(1) 
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
        layout.addWidget(QLabel('DAC:'))
        layout.addWidget(self.dacLabel)
        layout.addStretch(1) 
        self.bottomLeftGroupBox.setLayout(layout)

    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox = QGroupBox("Group 3")
        self.bottomRightGroupBox.setCheckable(True)
        self.bottomRightGroupBox.setChecked(True)

        lineEdit = QLineEdit('s3cRe7')
        lineEdit.setEchoMode(QLineEdit.Password)

        spinBox = QSpinBox(self.bottomRightGroupBox)
        spinBox.setValue(50)

        dateTimeEdit = QDateTimeEdit(self.bottomRightGroupBox)
        dateTimeEdit.setDateTime(QDateTime.currentDateTime())

        slider = QSlider(Qt.Horizontal, self.bottomRightGroupBox)
        slider.setValue(40)

        scrollBar = QScrollBar(Qt.Horizontal, self.bottomRightGroupBox)
        scrollBar.setValue(60)

        dial = QDial(self.bottomRightGroupBox)
        dial.setValue(30)
        dial.setNotchesVisible(True)

        layout = QGridLayout()
        layout.addWidget(lineEdit, 0, 0, 1, 2)
        layout.addWidget(spinBox, 1, 0, 1, 2)
        layout.addWidget(dateTimeEdit, 2, 0, 1, 2)
        layout.addWidget(slider, 3, 0)
        layout.addWidget(scrollBar, 4, 0)
        layout.addWidget(dial, 3, 1, 2, 1)
        layout.setRowStretch(5, 1)
        self.bottomRightGroupBox.setLayout(layout)

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
        ser = serial.Serial('COM6')
        ser.write(b'1')  # 1 = duty change
        ser.write(b'1') # 1 = decrease duty
        self.dutyLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def incDuty(self):
        print("increase")
        ser = serial.Serial('COM6')
        ser.write(b'1')  # 1 = duty change
        ser.write(b'2') # 2 = increase duty
        self.dutyLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def decFreq(self):
        print("decrease")
        ser = serial.Serial('COM6')
        ser.write(b'2')  # 2 = freq change
        ser.write(b'1') # 1 = decrease freq
        self.freqLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def incFreq(self):
        print("increase")
        ser = serial.Serial('COM6')
        ser.write(b'2')  # 2 = freq change
        ser.write(b'2') # 2 = increase freq
        self.freqLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def decDac(self):
        print("decrease")
        ser = serial.Serial('COM6')
        ser.write(b'3')  # 2 = freq change
        ser.write(b'1') # 1 = decrease freq
        self.dacLabel.setText(ser.readline().decode("utf-8"))
        ser.close()

    @pyqtSlot()
    def incDac(self):
        print("increase")
        ser = serial.Serial('COM6')
        ser.write(b'3')  # 2 = dac change
        ser.write(b'2') # 2 = increase dac
        self.dacLabel.setText(ser.readline().decode("utf-8"))
        ser.close()


if __name__ == '__main__':

    import sys
    import serial

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()

    gallery.freqLabel.setText("200" + " Hz")

    sys.exit(app.exec_()) 

    ser.close()