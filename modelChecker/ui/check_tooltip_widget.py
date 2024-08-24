from PySide6 import QtWidgets, QtCore

class CheckTooltipWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, text=""):
        super().__init__(parent, QtCore.Qt.ToolTip)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.ToolTip)
        self.setStyleSheet("background-color: #333; color: white; border-radius: 5px; padding: 8px;")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel(text)
        self.layout.addWidget(self.label)
        self.setVisible(False)
    
    def set_text(self, text):
        self.label.setText(text)
    
    def show_tooltip(self, position):
        self.move(position)
        self.setVisible(True)
    
    def hide_tooltip(self):
        self.setVisible(False)