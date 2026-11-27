import sys
import random
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
from PyQt5.QtCore import pyqtSlot, QFile, QTextStream, QTimer
from PyQt5 import QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import plotswidget as pltw

if __name__ == "__main__":
	app = QApplication(sys.argv)

	# Create a Qt widget, which will be our window.
	window = pltw.MainWindow()
	window.show()  # IMPORTANT!!!!! Windows are hidden by default.

	# Start the event loop.
	app.exec()