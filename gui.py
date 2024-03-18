from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import *
import sys

import quaternion
from comet_plot import CometPlotWidget
from comm_zmq import get_subscriber_sock
from live_plot import LivePlot
from orientation_visulization import OrientationVisualizer

ZMQ_PORT = 5555

class InfoTab(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        header1_font = QFont('Roboto', 20)
        header2_font = QFont('Roboto', 14)
        style_sheet = "background-color: lightgray; border-radius: 15px;"

        left_col = QVBoxLayout()
        left_col.setContentsMargins(30,30,30,30)

        self.position_label = QLabel("Position\nX:\nY:\nZ:")
        self.position_label.setWordWrap(True)
        self.position_label.setFont(header1_font)
        self.position_label.setContentsMargins(20,10,20,10)
        self.position_label.setStyleSheet(style_sheet)
        left_col.addWidget(self.position_label)

        left_col.addSpacing(30)

        self.velocity_label = QLabel("Velocity\nX:\nY:\nZ:")
        self.velocity_label.setWordWrap(True)
        self.velocity_label.setFont(header1_font)
        self.velocity_label.setContentsMargins(20,10,20,10)
        self.velocity_label.setStyleSheet(style_sheet)
        left_col.addWidget(self.velocity_label)

        left_col.addSpacing(30)

        self.gyro_bias_label = QLabel("Gyro bias: ")
        self.gyro_bias_label.setWordWrap(True)
        self.gyro_bias_label.setFont(header2_font)
        self.gyro_bias_label.setContentsMargins(20,10,20,10)
        self.gyro_bias_label.setStyleSheet(style_sheet)
        left_col.addWidget(self.gyro_bias_label)

        left_col.setAlignment(Qt.AlignTop)
    
        
        right_col = QVBoxLayout()
        right_col.setContentsMargins(30,30,30,30)

        orientation_layout = QVBoxLayout()
        orientation_label = QLabel("Orientation")
        orientation_label.setAlignment(Qt.AlignLeft)
        orientation_label.setFont(header2_font)
        orientation_layout.addWidget(orientation_label, 1)
        self.orientation_vis = OrientationVisualizer()
        orientation_layout.addWidget(self.orientation_vis, 9)
        orientation_widget = QWidget()
        orientation_widget.setLayout(orientation_layout)
        orientation_widget.setContentsMargins(20,10,20,10)
        orientation_widget.setStyleSheet(style_sheet)
        right_col.addWidget(orientation_widget,1)

        preview_layout = QVBoxLayout()
        preview_label = QLabel("Preview (XY plane)")
        preview_label.setAlignment(Qt.AlignLeft)
        preview_label.setFont(header2_font)
        preview_layout.addWidget(preview_label, 1)
        self.preview_plot = CometPlotWidget(title="", max_points=500, bg_color="w")
        preview_layout.addWidget(self.preview_plot, 9)
        preview_widget = QWidget()
        preview_widget.setLayout(preview_layout)
        preview_widget.setContentsMargins(20,10,20,10)
        preview_widget.setStyleSheet(style_sheet)
        right_col.addWidget(preview_widget,1)

        columns = QHBoxLayout()
        columns.addLayout(left_col, 3)
        columns.addLayout(right_col, 2)
        self.setLayout(columns)

        self.socket_state = get_subscriber_sock(ZMQ_PORT,"s")

        self.timer = QTimer(self)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def parse_state(self, payload):
        tokens = [float(elem) for elem in payload[2:].split(",")]
        position = tokens[0:3]
        velocity = tokens[3:6]
        orientation = tokens[6:10]
        gyro_bias = tokens[10:13]
        return (position, velocity, orientation, gyro_bias)

    def update(self):
        try:
            s = self.socket_state.recv_string()
            position, velocity, orientation, gyro_bias = self.parse_state(s)
            self.position_label.setText(f"Position\nX: {position[0]}\nY: {position[1]}\nZ: {position[2]}")
            self.velocity_label.setText(f"Velocity\nX: {velocity[0]}\nY: {velocity[1]}\nZ: {velocity[2]}")
            self.gyro_bias_label.setText(f"Gyro bias: {gyro_bias}")
            self.orientation_vis.rotate(quaternion.from_float_array(orientation))
            self.preview_plot.append(position[0], position[1])
        except:
            pass

class SensorTab(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        columns = QHBoxLayout()
        self.accel_live_plot = LivePlot(max_points=100, num_lines=3, title="Accelerometer", bg_color="w")
        columns.addWidget(self.accel_live_plot)
        self.gyro_live_plot = LivePlot(max_points=100, num_lines=3, title="Gyroscope", bg_color="w")
        columns.addWidget(self.gyro_live_plot)
        self.setLayout(columns)

        self.socket_gyro = get_subscriber_sock(ZMQ_PORT,"g")
        self.socket_accel = get_subscriber_sock(ZMQ_PORT,"a")

        self.timer = QTimer(self)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def update(self):
        try:
            s = self.socket_accel.recv_string()
            tokens = [float(elem) for elem in s[2:].split(",")]
            self.accel_live_plot.append(tokens[0]/1000.0, tokens[1:])
        except:
            pass
        try:
            s = self.socket_gyro.recv_string()
            tokens = [float(elem)/1000.0 for elem in s[2:].split(",")]
            self.gyro_live_plot.append(tokens[0], tokens[1:])
        except:
            pass
    
    def __del__(self):
        pass

class ForceTab(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.NO_OF_COLUMNS = 3
        self.no_of_sensors = 0
        self.plots = []
        self.prepare_layout(6)

        self.socket_force = get_subscriber_sock(ZMQ_PORT,"f")

        self.timer = QTimer(self)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def update_plots(self, time, forces):
        self.prepare_layout(len(forces))
        for (i,elem) in enumerate(forces):
            self.plots[i].append(time, elem)
        pass

    def prepare_layout(self, no_of_sensors):
        if no_of_sensors == self.no_of_sensors:
            return
        
        while self.no_of_sensors > no_of_sensors:
            self.plots.pop()
            self.no_of_sensors -= 1
        while self.no_of_sensors < no_of_sensors:
            self.plots.append(LivePlot(max_points=100, num_lines=1, title=f"Force {self.no_of_sensors+1}", bg_color="w"))
            self.no_of_sensors += 1

        columns = []
        for i in range(self.NO_OF_COLUMNS):
            columns.append(QVBoxLayout())
        
        for i in range(self.no_of_sensors):
            columns[i % self.NO_OF_COLUMNS].addWidget(self.plots[i])
        
        layout = QHBoxLayout()
        for i in range(self.NO_OF_COLUMNS):
            layout.addLayout(columns[i])
        
        self.setLayout(layout)

    def update(self):
        try:
            s = self.socket_force.recv_string()
            tokens = [float(elem) for elem in s[2:].split(",")]
            time = tokens[0]
            forces = tokens[1:]
            self.update_plots(time, forces)
        except:
            pass

class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super(Highlighter, self).__init__(parent)
        self.error_format = QTextCharFormat()
        self.error_format.setBackground(Qt.red)
        self.debug_format = QTextCharFormat()
        self.debug_format.setBackground(Qt.darkMagenta)

    def highlightBlock(self, text):
        if("ERROR" in text):
            self.setFormat(0, len(text), self.error_format)
        if("DEBUG" in text):
            self.setFormat(0, len(text), self.debug_format)

class ConsoleTab(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        header2_font = QFont('Roboto', 20)
        self.setContentsMargins(30,30,30,30)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("background-color: lightgray;")
        self.highlighter = Highlighter(self.text_edit.document())

        layout = QVBoxLayout()
        console_label = QLabel("Console")
        console_label.setFont(header2_font)
        layout.addWidget(console_label)
        layout.addWidget(self.text_edit)
        
        self.setLayout(layout)

        self.socket_console = get_subscriber_sock(6666,"c", False)

        self.timer = QTimer(self)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update)
        self.timer.start()
    
    def update(self):
        try:
            s = self.socket_console.recv_string()
            self.text_edit.append(s[2:])
        except:
            pass
        

class GUI(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.closed = False
        self.resize(1280, 960)
        self.setWindowIcon(QIcon('logo.png'))
        self.setWindowTitle('MEiL-NAV')

        self.info_tab = InfoTab()
        self.sensor_tab = SensorTab()
        self.force_tab = ForceTab()
        self.console_tab = ConsoleTab()
        self.action_tab = QWidget()
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self.info_tab, "Info")
        self.tabs.addTab(self.sensor_tab, "Sensors")
        self.tabs.addTab(self.force_tab, "Forces")
        self.tabs.addTab(self.action_tab, "Actions")
        self.tabs.addTab(self.console_tab, "Console")

        self.setCentralWidget(self.tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GUI()
    win.show()
    sys.exit(app.exec_())
    