#!/usr/bin/env python
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

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

def decDuty():
    print(1) # 1 = duty cycle change
    print(0) # 0 = decrease duty cycle

def incDuty():
    print(1) # 1 = duty cycle change
    print(1) # 1 = increase duty cycle

def setupTabs(tabWidget):

    # tab 1
    tab1 = QWidget()
    tab1grid = QGridLayout()

    tab1grid.setContentsMargins(5,5,5,5)
    tab1.setLayout(tab1grid)

    # tab 2
    tab2 = QWidget()
    tab2hbox = QHBoxLayout()
    tab2hbox.setContentsMargins(5,5,5,5)
    tab2.setLayout(tab2hbox)

    # add tabs
    tabWidget.addTab(tab1, "Change Duty Cycle")
    tabWidget.addTab(tab2, "Change Frequency")

if __name__ == '__main__':

    print('HELLO')
    import sys
    import serial

    # serial test
    # ser = serial.Serial('COM6')
    # print(ser.name)
    # ser.write(b'4')

    app = QApplication(sys.argv)

    # widgets
    window = QWidget()
    tabWidget = QTabWidget()

    # setup tabs
    setupTabs(tabWidget)

    # set layout
    layout = QVBoxLayout()
    window.setLayout(layout)

    # add widgets
    layout.addWidget(tabWidget)

    # window settings and show
    window.setWindowTitle("Nexsonic UDTS")
    window.setFixedSize(600,400)
    window.show()

    # end app
    sys.exit(app.exec_()) 

    # close serial port
    # ser.close()

