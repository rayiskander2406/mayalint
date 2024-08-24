from PySide6 import QtWidgets, QtCore
        
PRESETS_EXAMPLES = ["Character Modelling", "Environment", "Vehicles"]

class SettingsUI(QtWidgets.QWidget):
    change_preset_signal = QtCore.Signal(object)
    
    def __init__(self):
        super().__init__()
        
        self.settings_expanded = False
        self.preset = "Character Modeling"
        
        self._build_preset_ui()
        
        settings_layout = QtWidgets.QVBoxLayout(self)
        
        self.settings_widget = QtWidgets.QWidget()
        self.settings_widget.setVisible(self.settings_expanded)
        expanded_settings_layout = QtWidgets.QVBoxLayout(self.settings_widget)
        
        data_type_settings_widget = QtWidgets.QWidget()
        data_type_settings_layout = QtWidgets.QHBoxLayout(data_type_settings_widget)
        
        data_type_settings_layout.addWidget(QtWidgets.QLabel("Maya or USD?"))
        
        expanded_settings_layout.addWidget(data_type_settings_widget)
        
        settings_layout.addWidget(self.preset_widget)
        settings_layout.addWidget(self.settings_widget)
    
    def _build_preset_ui(self):
        self.preset_widget = QtWidgets.QWidget()
        
        preset_layout = QtWidgets.QHBoxLayout(self.preset_widget)

        combo_box = QtWidgets.QComboBox(self)
        combo_box.addItems(PRESETS_EXAMPLES)
        
        settings_button = QtWidgets.QPushButton("\u2699")
        settings_button.setMaximumWidth(30)
        settings_button.clicked.connect(self.toggle_settings)
        
        preset_layout.addWidget(QtWidgets.QLabel("Preset: "))
        preset_layout.addWidget(combo_box,1)
        preset_layout.addWidget(settings_button)
        
    def toggle_settings(self):
        self.settings_expanded = not self.settings_expanded
        self.settings_widget.setVisible(self.settings_expanded)
    