import sys
import time
import zmq
from PyQt5 import QtWidgets

from live_plot import LivePlotWindow
from orientation_visulization import OrientationVisualizerWindow
from comm_zmq import get_subscriber_sock

socket_gyro = get_subscriber_sock(5555,"g")
socket_accel = get_subscriber_sock(5555,"a")
socket_state = get_subscriber_sock(5555,"s")

def parse_state(payload):
    tokens = [float(elem) for elem in payload[2:].split(",")]
    position = tokens[0:3]
    velocity = tokens[3:6]
    orientation = tokens[6:10]
    gyro_bias = tokens[10:13]
    return (position, velocity, orientation, gyro_bias)



app = QtWidgets.QApplication(sys.argv)

window_accelerometer = LivePlotWindow(title="Accelerometer", num_lines=3)
window_accelerometer.show()

window_gyroscope = LivePlotWindow(title="Gyroscope", num_lines=3)
window_gyroscope.show()

window_visualization = OrientationVisualizerWindow()
window_visualization.show()

while not window_accelerometer.is_closed() or not window_gyroscope.is_closed() or not window_visualization.is_closed():

    try:
        s = socket_accel.recv_string()
        tokens = [float(elem) for elem in s[2:].split(",")]
        window_accelerometer.update_plot(tokens[0]/1000.0, tokens[1:])
        #print(s)
    except:
        pass
    try:
        s = socket_gyro.recv_string()
        tokens = [float(elem)/1000.0 for elem in s[2:].split(",")]
        window_gyroscope.update_plot(tokens[0], tokens[1:]) # [elem/1000.0 for elem in  tokens[1:]])
        #print(s)
    except:
        pass
    try:
        s = socket_state.recv_string()
        position, velocity, orientation, gyro_bias = parse_state(s)
        window_visualization.update(orientation)
    except:
        pass
    
    app.processEvents()
    time.sleep(0.001)

socket_gyro.close()
socket_accel.close()