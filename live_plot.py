import sys
import time
import numpy as np
from PyQt6 import QtWidgets
import pyqtgraph as pg

class LivePlot(QtWidgets.QWidget):
    def __init__(self, parent=None, max_points=100, num_lines=3, title="Live plot", bg_color="k"):
        super(LivePlot, self).__init__(parent)

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        self.plot_widget = pg.PlotWidget(title=title)
        self.plot_widget.setBackground(bg_color)
        self.plot_widget.showGrid(x=True, y=True)
        self.max_points = max_points
        self.num_lines = num_lines
        self.curves = [self.plot_widget.plot(pen=pg.mkPen(color, width=1)) for color in colors]
        if num_lines == 3:
            legend = self.plot_widget.plotItem.addLegend()
            legend.addItem(self.curves[0], "X")
            legend.addItem(self.curves[1], "Y")
            legend.addItem(self.curves[2], "Z")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
        self.clear_plot()

    def clear_plot(self):
        self.data = np.zeros((self.max_points, self.num_lines + 1))
        self.data_start_index = self.max_points
        self.update_plot()

    def append(self, time, values):
        self.data = np.roll(self.data, -1, axis=0)
        self.data[-1, 0] = time
        self.data[-1, 1:] = values
        if self.data_start_index > 0:
            self.data_start_index = self.data_start_index - 1 
        self.update_plot()

    def update_plot(self):
        for i in range(self.num_lines):
            self.curves[i].setData(self.data[self.data_start_index:, 0], self.data[self.data_start_index:, i+1])

class LivePlotWindow(QtWidgets.QMainWindow):
    def __init__(self, max_points=100, num_lines=3, title="Live plot", bg_color="k"):
        super(LivePlotWindow, self).__init__()
        self.closed = False

        self.live_plot = LivePlot(max_points=max_points, num_lines=num_lines, title=title, bg_color=bg_color)
        self.setCentralWidget(self.live_plot)

        # Clear button
        toolbar = self.addToolBar("Toolbar")
        clear_button = QtWidgets.QPushButton("Clear Plot", self)
        clear_button.clicked.connect(self.live_plot.clear_plot)
        toolbar.addWidget(clear_button)

    def update_plot(self, time, values):
        self.live_plot.append(time, values)
    
    def closeEvent(self, event):
        self.closed = True

    def is_closed(self):
        return self.closed

# Example
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window1 = LivePlotWindow(title="Plot 1", num_lines=3)
    window1.show()

    window2 = LivePlotWindow(title="Plot 2", num_lines=2)
    window2.show()

    i = 0
    while not window1.is_closed() or not window2.is_closed():
        values1 = np.random.randint(0, 50, size=(3,))
        values2 = np.random.randint(0, 50, size=(2,))

        window1.update_plot(i, values1)
        window2.update_plot(i, values2)
        i = i + 1

        app.processEvents()
        time.sleep(0.1)
