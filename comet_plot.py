import math
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg
import numpy as np

class CometPlotWidget(QWidget):
    def __init__(self, parent=None, max_points=100, title="Comet plot", bg_color="k"):
        super(CometPlotWidget, self).__init__(parent)

        self.layout = QVBoxLayout(self)

        self.plot_widget = pg.PlotWidget(title=title)
        self.plot_widget.setBackground(bg_color)
        self.plot_widget.showGrid(x=True, y=True) 
        self.max_points = max_points  
        self.layout.addWidget(self.plot_widget)
        self.plot_data = self.plot_widget.plot(pen=pg.mkPen('r', width = 2))
        # self.plot_widget.setRange(xRange=[-1, 1], yRange=[-1, 1])
        self.clear_plot()

    def clear_plot(self):
        self.data = np.zeros((self.max_points, 2))
        self.data_start_index = self.max_points
        self.update_plot()

    def append(self, x, y):
        self.data = np.roll(self.data, -1, axis=0)
        self.data[-1, 0] = x
        self.data[-1, 1:] = y
        if self.data_start_index > 0:
            self.data_start_index = self.data_start_index - 1 
        self.update_plot()

    def set_range(self, x_min, x_max, y_min, y_max):
        self.plot_widget.setRange(xRange=[x_min, x_max], yRange=[y_min, y_max])

    def update_plot(self):
        self.plot_data.setData(self.data[self.data_start_index:, 0], self.data[self.data_start_index:, 1])

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.comet_plot_widget = CometPlotWidget()
        self.setCentralWidget(self.comet_plot_widget)

        self.data_index = 0

    def update_plot(self):
        x = math.cos(self.data_index)
        y = math.sin(self.data_index)
        self.comet_plot_widget.append(x, y)
        self.data_index += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(main.update_plot)
    timer.start(50)

    sys.exit(app.exec_())