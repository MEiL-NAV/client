import sys
import time
import zmq
from PyQt5 import QtWidgets

from live_plot import LivePlotWindow

context = zmq.Context()
socket_gyro = context.socket(zmq.SUB)
socket_gyro.set(zmq.CONFLATE,1)
socket_gyro.set(zmq.RCVTIMEO,10)
socket_gyro.connect("tcp://localhost:5555")
socket_gyro.subscribe("g")
socket_accel = context.socket(zmq.SUB)
socket_accel.set(zmq.CONFLATE,1)
socket_accel.set(zmq.RCVTIMEO,10)
socket_accel.connect("tcp://localhost:5555")
socket_accel.subscribe("a")


app = QtWidgets.QApplication(sys.argv)

window_accelerometer = LivePlotWindow(title="Accelerometer", num_lines=3)
window_accelerometer.show()

window_gyroscope = LivePlotWindow(title="Gyroscope", num_lines=3)
window_gyroscope.show()

while not window_accelerometer.is_closed() or not window_gyroscope.is_closed():

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

    app.processEvents()
    time.sleep(0.001)

socket_gyro.close()
socket_accel.close()