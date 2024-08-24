from PySide6 import QtWidgets

class ProgressUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        
        
    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        
        self.node_progress = QtWidgets.QProgressBar()
        self.checks_progress = QtWidgets.QProgressBar()
        
        main_layout.addWidget(self.node_progress)
        main_layout.addWidget(self.checks_progress)
        
    def update(self, data):
        if "nodes_total" in data and "current_node" in data:
            self.node_progress.setMaximum(data["nodes_total"])
            self.node_progress.setValue(data["current_node"])
        
        if "total_checks" in data and "current_check" in data:
            self.checks_progress.setMaximum(data["total_checks"])
            self.checks_progress.setValue(data["current_check"])
    
    def reset(self):
        self.node_progress.reset()
        self.checks_progress.reset()