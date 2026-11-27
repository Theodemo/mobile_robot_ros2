import sys
import random
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


### Tutorial & Source: https://www.pythonguis.com/tutorials/plotting-matplotlib/

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=1, height=2, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.motor_axes = fig.add_subplot(211) 
        self.robot_axes = fig.add_subplot(212)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.setCentralWidget(self.canvas)

        n_data = 50
        self.te_ms = 0.1
        self.xmotor = list(range(n_data))
        self.yleftspeed = [random.randint(0, 200) for i in range(n_data)]
        self.yrightspeed = [random.randint(0, 200) for i in range(n_data)]
        self.ileft = 0
        self.iright = 0

        self.xrobot = list(range(-n_data, 0))
        self.yrobotspeed = [0]*n_data
        self.irobot = 0

        toolbar = NavigationToolbar(self.canvas, self)

        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        self._motorplot_left_ref = None
        self._motorplot_right_ref = None
        self._robotplot_ref = None

        self.update_speed(0, n_data, "Left")
        self.update_speed(0, n_data, "Right")

        self.update_robotspeed(0, 0)

        self.show()

    def update_speed(self, nval, ntime, side):
        self.xmotor = self.xmotor[1:] + [ntime]
        if (side == "Left"):
            self.yleftspeed = self.yleftspeed[1:] + [nval]
        elif (side == "Right"):
            self.xrightspeed = self.yrightspeed[1:] + [nval]

        if ((self._motorplot_right_ref) or (self._motorplot_left_ref)) is None:
            plot_refs_left = self.canvas.motor_axes.plot(self.xmotor,
                                              self.yleftspeed,
                                              'r',
                                              marker = 'x',
                                              label = "Left")
            self._motorplot_left_ref = plot_refs_left[0]

            plot_refs_right = self.canvas.motor_axes.plot(self.xmotor,
                                              self.yrightspeed,
                                              'b',
                                              marker = 'x',
                                              label = "right")
            self._motorplot_right_ref = plot_refs_right[0]
        else:
            
            self._motorplot_left_ref.set_xdata(self.xmotor)
            self._motorplot_right_ref.set_xdata(self.xmotor)

            self._motorplot_left_ref.set_ydata(self.yleftspeed)
            self._motorplot_right_ref.set_ydata(self.yrightspeed)

        self.canvas.draw()
    def update_robotspeed(self, nval, ntime):
        self.xrobot = self.xrobot[1:] + [ntime]
        self.yrobotspeed = self.yrobotspeed[1:] + [nval]

        if self._robotplot_ref is None :
            plot_refs = self.canvas.robot_axes.plot(self.xrobot, self.yrobotspeed,
                                                    marker = 'x',
                                                    label = 'robot')
            self._robotplot_ref = plot_refs[0]
        else:
            self._robotplot_ref.set_xdata(self.xrobot)
            self._robotplot_ref.set_ydata(self.yrobotspeed)

        self.canvas.draw()

class PlotsWidgets(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(PlotsWidgets, self).__init__(*args, **kwargs)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.setCentralWidget(self.canvas)

        n_data = 50
        self.te_ms = 0.1
        self.xmotor = list(range(n_data))
        self.yleftspeed = [random.randint(0, 200) for i in range(n_data)]
        self.yrightspeed = [random.randint(0, 200) for i in range(n_data)]
        self.ileft = 0
        self.iright = 0

        self.xrobot = list(range(-n_data, 0))
        self.yrobotspeed = [0]*n_data
        self.irobot = 0

        toolbar = NavigationToolbar(self.canvas, self)

        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        self._motorplot_left_ref = None
        self._motorplot_right_ref = None
        self._robotplot_ref = None

        self.update_speed(0, n_data, "Left")
        self.update_speed(0, n_data, "Right")

        self.update_robotspeed(0, 0)

        self.show()

    def update_speed(self, nval, ntime, side):
        self.xmotor = self.xmotor[1:] + [ntime]
        if (side == "Left"):
            self.yleftspeed = self.yleftspeed[1:] + [nval]
        elif (side == "Right"):
            self.xrightspeed = self.yrightspeed[1:] + [nval]

        if ((self._motorplot_right_ref) or (self._motorplot_left_ref)) is None:
            plot_refs_left = self.canvas.motor_axes.plot(self.xmotor,
                                              self.yleftspeed,
                                              'r',
                                              marker = 'x',
                                              label = "Left")
            self._motorplot_left_ref = plot_refs_left[0]

            plot_refs_right = self.canvas.motor_axes.plot(self.xmotor,
                                              self.yrightspeed,
                                              'b',
                                              marker = 'x',
                                              label = "right")
            self._motorplot_right_ref = plot_refs_right[0]
        else:
            
            self._motorplot_left_ref.set_xdata(self.xmotor)
            self._motorplot_right_ref.set_xdata(self.xmotor)

            self._motorplot_left_ref.set_ydata(self.yleftspeed)
            self._motorplot_right_ref.set_ydata(self.yrightspeed)

        self.canvas.draw()
    def update_robotspeed(self, nval, ntime):
        self.xrobot = self.xrobot[1:] + [ntime]
        self.yrobotspeed = self.yrobotspeed[1:] + [nval]

        if self._robotplot_ref is None :
            plot_refs = self.canvas.robot_axes.plot(self.xrobot, self.yrobotspeed,
                                                    marker = 'x',
                                                    label = 'robot')
            self._robotplot_ref = plot_refs[0]
        else:
            self._robotplot_ref.set_xdata(self.xrobot)
            self._robotplot_ref.set_ydata(self.yrobotspeed)

        self.canvas.draw()
'''
class PlotsWidgets(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(PlotsWidgets, self).__init__(*args, **kwargs)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        #self.setCentralWidget(self.canvas)

        n_data = 50
        self.te_ms = 0.1
        self.xmotor = list(range(n_data))
        self.yleftspeed = [random.randint(0, 200) for i in range(n_data)]
        self.yrightspeed = [random.randint(0, 200) for i in range(n_data)]
        self.ileft = 0
        self.iright = 0

        self.xrobot = list(range(-n_data, 0))
        self.yrobotspeed = [0]*n_data
        self.irobot = 0

        toolbar = NavigationToolbar(self.canvas, self)

        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        self._motorplot_left_ref = None
        self._motorplot_right_ref = None
        self._robotplot_ref = None

        self.update_speed(0, n_data, "Left")
        self.update_speed(0, n_data, "Right")

        self.update_robotspeed(0, 0)

        self.show()

    def update_speed(self, nval, ntime, side):
        self.xmotor = self.xmotor[1:] + [ntime]
        if (side == "Left"):
            self.yleftspeed = self.yleftspeed[1:] + [nval]
        elif (side == "Right"):
            self.xrightspeed = self.yrightspeed[1:] + [nval]

        if ((self._motorplot_right_ref) or (self._motorplot_left_ref)) is None:
            plot_refs_left = self.canvas.motor_axes.plot(self.xmotor,
                                              self.yleftspeed,
                                              'r',
                                              marker = 'x',
                                              label = "Left")
            self._motorplot_left_ref = plot_refs_left[0]

            plot_refs_right = self.canvas.motor_axes.plot(self.xmotor,
                                              self.yrightspeed,
                                              'b',
                                              marker = 'x',
                                              label = "right")
            self._motorplot_right_ref = plot_refs_right[0]
        else:
            
            self._motorplot_left_ref.set_xdata(self.xmotor)
            self._motorplot_right_ref.set_xdata(self.xmotor)

            self._motorplot_left_ref.set_ydata(self.yleftspeed)
            self._motorplot_right_ref.set_ydata(self.yrightspeed)

        self.canvas.draw()
    def update_robotspeed(self, nval, ntime):
        self.xrobot = self.xrobot[1:] + [ntime]
        self.yrobotspeed = self.yrobotspeed[1:] + [nval]

        if self._robotplot_ref is None :
            plot_refs = self.canvas.robot_axes.plot(self.xrobot, self.yrobotspeed,
                                                    marker = 'x',
                                                    label = 'robot')
            self._robotplot_ref = plot_refs[0]
        else:
            self._robotplot_ref.set_xdata(self.xrobot)
            self._robotplot_ref.set_ydata(self.yrobotspeed)

        self.canvas.draw()
'''

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = PlotsWidgets()
    app.exec_()