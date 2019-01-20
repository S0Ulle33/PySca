import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from main_ui import *
import MainPresenter


class MyWin(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.presenter = MainPresenter.MainPresenter(self.ui)
        self.ui.startButton.clicked.connect(self.startButtonClicked)
        self.isScanActive = False

    def startButtonClicked(self):
        if self.isScanActive == False:
            self.isScanActive = True
            self.ui.startButton.setText("Stop")
            self.presenter.startScan(self.ui.ipLine.text(), self.ui.portsLine.text(), self.ui.threadsLine.text(),
                                     self.ui.timeoutLine.text())
        else:
            self.isScanActive = False
            self.ui.startButton.setText("Start")
            self.presenter.stopScan()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
