"""
An example of using WinGrab in the sub thread with PyQt5.

The code in this example is the same as the code in examples/pyqt5_example.py, except that the grab function is called
in another thread.

You can create a thread for `wingrab` by using the `threading` module or the `QThread` class.

This example is only for demonstration purposes. It is not recommended to use this example directly in your project.

@Author: Jianzhang Chen
"""

from PyQt5 import QtWidgets, QtCore

# You can change this to PySide2 if you want to use PySide2.
# from PySide2 import QtWidgets, QtCore

# If you import wingrab in another thread, you will get an error!
# You can import wingrab in the main thread and use it in another thread.
import wingrab


class ExampleWindow(QtWidgets.QMainWindow):
    # The signal is used to notify the main thread that the grab is finished.
    _sigGrabFinished = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("WinGrab Example Window")
        self.resize(400, 300)
        self.setMouseTracking(True)

        self._mainLayout = QtWidgets.QVBoxLayout()
        self._mainLayout.setContentsMargins(0, 0, 0, 0)
        self._mainLayout.setSpacing(0)

        self._pidLabel = QtWidgets.QLabel(self)
        self._pidLabel.setAlignment(QtCore.Qt.AlignCenter)
        self._pidLabel.setStyleSheet("background-color: rgb(255, 255, 255);")
        self._pidLabel.setText("PID: ")

        self._grabButton = QtWidgets.QPushButton(self)
        self._grabButton.setText("Grab")
        self._grabButton.setFixedHeight(40)
        self._grabButton.clicked.connect(self._startGrab)

        self._mainLayout.addWidget(self._pidLabel)
        self._mainLayout.addWidget(self._grabButton)

        self._centralWidget = QtWidgets.QWidget(self)
        self._centralWidget.setLayout(self._mainLayout)
        self.setCentralWidget(self._centralWidget)

        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(1_000)
        self._timer.timeout.connect(self._setLoadingText)

        self._sigGrabFinished.connect(self._onGrabFinished)

    def _grabInSubThread(self):
        """ Grab in another thread. """
        pid = wingrab.grab()
        self._pidLabel.setText(f"PID: {pid}")

    def _startGrab(self):
        self._timer.start()
        self._setLoadingText()

        thread = QtCore.QThread(self)
        thread.started.connect(self._grabInSubThread)
        thread.finished.connect(thread.deleteLater)
        thread.start()

        # You can also use the `threading` module to create a thread.
        # thread = threading.Thread(target=self._grabInSubThread)
        # thread.start()

        self._timer.stop()

    def _setLoadingText(self):
        self._pidLabel.setText(f"PID: Loading... (Current Time: {QtCore.QTime.currentTime().toString('hh:mm:ss')})")

    def _onGrabFinished(self, pid: int):
        self._pidLabel.setText(f"PID: {pid}")
        self._timer.stop()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = ExampleWindow(None)
    window.show()
    sys.exit(app.exec_())
