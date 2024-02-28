from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from PyQt5 import QtOpenGL
import OpenGL.GL as gl
from OpenGL import GLU
import numpy as np
import sys
import quaternion


class OrientationVisualizer(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.rot_angle = 0
        self.rot_axis = [0, 0, 1]

        # self.timer = QTimer(self)
        # self.timer.setInterval(20)
        # self.timer.timeout.connect(self.updateGL)
        # self.timer.start()
            
    def initializeGL(self):
        self.qglClearColor(QColor(255, 255, 255)) # light gray background
        gl.glEnable(gl.GL_DEPTH_TEST)
         
    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glLoadIdentity()    
        aspect = width / float(height)
        GLU.gluPerspective(45.0, aspect, 1.0, 100.0)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glPushMatrix()

        gl.glTranslate(0.0, 00.0, -50.0)
        gl.glScale(15.0, 15.0, 15.0)       
        gl.glRotate(self.rot_angle, *self.rot_axis)
        # gl.glRotate(30, 1.0, 0.0, 0.0)
        # gl.glTranslate(-0.5, -0.5, -0.5)

        # Draw X arrow (red)
        gl.glColor3f(1.0, 0.0, 0.0)  # Red
        self.drawArrow([0.0, 0.0, 0.0], [0.0, 0.0, 1.0])

        # Draw Y arrow (green)
        gl.glColor3f(0.0, 1.0, 0.0)  # Green
        self.drawArrow([0.0, 0.0, 0.0], [1.0, 0.0, 0.0])

        # Draw Z arrow (blue)
        gl.glColor3f(0.0, 0.0, 1.0)  # Blue
        self.drawArrow([0.0, 0.0, 0.0], [0.0, 1.0, 0.0])

        gl.glPopMatrix()

    def drawArrow(self, start, end):
        # Draw a line from start to end
        gl.glLineWidth(2)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex3fv(start)
        gl.glVertex3fv(end)
        gl.glEnd()

        # Draw arrowhead
        direction = np.array(end) - np.array(start)
        arrowhead_size = np.linalg.norm(direction) / 5.0
        direction /= np.linalg.norm(direction)

        gl.glPushMatrix()
        gl.glTranslatef(end[0], end[1], end[2])

        # Calculate rotation angles
        theta = np.arctan2(direction[1], direction[0])
        phi = np.arcsin(direction[2])

        # Rotate arrowhead
        gl.glRotatef(np.degrees(theta), 0, 0, 1)
        gl.glRotatef(np.degrees(phi), 0, -1, 0)

        # Draw arrowhead
        gl.glBegin(gl.GL_TRIANGLES)
        gl.glVertex3f(arrowhead_size, 0, 0)
        gl.glVertex3f( 0, 0, -arrowhead_size / 5)
        gl.glVertex3f( 0, arrowhead_size / 5, 0)
        gl.glEnd()

        gl.glBegin(gl.GL_TRIANGLES)
        gl.glVertex3f(arrowhead_size, 0, 0)
        gl.glVertex3f( 0, 0, -arrowhead_size / 5)
        gl.glVertex3f( 0, -arrowhead_size / 5, 0)
        gl.glEnd()

        gl.glBegin(gl.GL_TRIANGLES)
        gl.glVertex3f(arrowhead_size, 0, 0)
        gl.glVertex3f( 0, 0, arrowhead_size / 5)
        gl.glVertex3f( 0, arrowhead_size / 5, 0)
        gl.glEnd()

        gl.glBegin(gl.GL_TRIANGLES)
        gl.glVertex3f(arrowhead_size, 0, 0)
        gl.glVertex3f( 0, 0, arrowhead_size / 5)
        gl.glVertex3f( 0, -arrowhead_size / 5, 0)
        gl.glEnd()

        gl.glPopMatrix()

    def rotate(self, quat):
        rot = quaternion.as_rotation_vector(quat)
        self.rot_axis = [rot[1], rot[2], rot[0]] / -np.linalg.norm(rot)
        self.rot_angle = np.degrees(np.linalg.norm(rot))
        self.updateGL()

        
class OrientationVisualizerWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.closed = False
        self.resize(500, 500)
        self.setWindowTitle('Orientation')

        self.glWidget = OrientationVisualizer(self)
        self.initGUI()
        self.resize(505,505)
        
    def initGUI(self):
        central_widget = QWidget()
        gui_layout = QVBoxLayout()
        central_widget.setLayout(gui_layout)
        self.setCentralWidget(central_widget)
        gui_layout.addWidget(self.glWidget)
        self.glWidget.paintGL()
    
    def update(self, quat):
        self.glWidget.rotate(quaternion.from_float_array(quat))
    
    def closeEvent(self, event):
        self.closed = True

    def is_closed(self):
        return self.closed



# Example        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = OrientationVisualizerWindow()
    win.show()
    sys.exit(app.exec_())
    