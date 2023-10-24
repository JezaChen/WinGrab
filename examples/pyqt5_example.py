"""
An example of using WinGrab with PyQt5.

This example is a simple window with a button. When the button is clicked, the PID of the window under the cursor will be
displayed in the window.

Note that the PID of the window under the cursor will be displayed as "Loading..." before the PID is obtained.

This example is only for demonstration purposes. It is not recommended to use this example directly in your project.

@Author: Jianzhang Chen
"""

from PyQt5 import QtWidgets, QtCore


# You can change this to PySide2 if you want to use PySide2.
# from PySide2 import QtWidgets, QtCore


class ExampleWindow(QtWidgets.QMainWindow):
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

    def _startGrab(self):
        self._timer.start()
        self._setLoadingText()

        import wingrab
        pid = wingrab.grab()

        self._pidLabel.setText(f"PID: {pid}")
        self._timer.stop()

    def _setLoadingText(self):
        self._pidLabel.setText(f"PID: Loading... (Current Time: {QtCore.QTime.currentTime().toString('hh:mm:ss')})")


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = ExampleWindow(None)
    window.show()
    sys.exit(app.exec_())
