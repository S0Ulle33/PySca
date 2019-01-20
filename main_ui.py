# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'nesca.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(422, 549)
        self.startButton = QtWidgets.QPushButton(Form)
        self.startButton.setGeometry(QtCore.QRect(140, 190, 131, 34))
        self.startButton.setObjectName("startButton")
        self.dataText = QtWidgets.QTextBrowser(Form)
        self.dataText.setGeometry(QtCore.QRect(0, 310, 421, 231))
        self.dataText.setObjectName("dataText")
        self.ipLine = QtWidgets.QLineEdit(Form)
        self.ipLine.setGeometry(QtCore.QRect(20, 70, 371, 34))
        self.ipLine.setObjectName("ipLine")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 50, 57, 18))
        self.label.setObjectName("label")
        self.portsLine = QtWidgets.QLineEdit(Form)
        self.portsLine.setGeometry(QtCore.QRect(20, 130, 371, 34))
        self.portsLine.setObjectName("portsLine")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(20, 110, 31, 18))
        self.label_2.setObjectName("label_2")
        self.threadsLine = QtWidgets.QLineEdit(Form)
        self.threadsLine.setGeometry(QtCore.QRect(20, 190, 113, 34))
        self.threadsLine.setObjectName("threadsLine")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(20, 170, 51, 18))
        self.label_3.setObjectName("label_3")
        self.timeoutLine = QtWidgets.QLineEdit(Form)
        self.timeoutLine.setGeometry(QtCore.QRect(280, 190, 113, 34))
        self.timeoutLine.setObjectName("timeoutLine")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(280, 170, 51, 18))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setGeometry(QtCore.QRect(20, 250, 101, 18))
        self.label_5.setObjectName("label_5")
        self.currentThreadsLabel = QtWidgets.QLabel(Form)
        self.currentThreadsLabel.setGeometry(QtCore.QRect(120, 250, 57, 18))
        self.currentThreadsLabel.setObjectName("currentThreadsLabel")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.startButton.setText(_translate("Form", "Start"))
        self.label.setText(_translate("Form", "IP Ranges"))
        self.label_2.setText(_translate("Form", "Ports"))
        self.label_3.setText(_translate("Form", "Threads"))
        self.label_4.setText(_translate("Form", "Timeout"))
        self.label_5.setText(_translate("Form", "Current threads: "))
        self.currentThreadsLabel.setText(_translate("Form", "0"))

