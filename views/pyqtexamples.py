import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QLabel, QGridLayout)
from PyQt5.QtGui import QPixmap
import pyqtgraph as pg
import pyqtgraph.examples
import qdarkstyle

class pyqtexamples(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        pyqtgraph.examples.run()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = pyqtexamples()
    window.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec_())

