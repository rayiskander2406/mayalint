from PySide6 import QtWidgets, QtCore

class ReportUI(QtWidgets.QWidget):
    verbosity_signal = QtCore.Signal()
    
    def __init__(self, consolidated_report = False):
        super().__init__()
        self.consolidated_report = consolidated_report
        self.verbosity_level = 0
        self._build_ui()
        
    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        
        report_style_widget = QtWidgets.QWidget()
        report_style_layout = QtWidgets.QHBoxLayout(report_style_widget)
        
        report_style_layout.addWidget(QtWidgets.QLabel("LOG Detail: "))
        
        self.level_combo_box = QtWidgets.QComboBox()
        self.level_combo_box.addItem("Overview")
        self.level_combo_box.addItem("Normal")
        self.level_combo_box.addItem("Verbose")
        self.level_combo_box.currentIndexChanged.connect(self.update_verbosity_level)

        
        report_style_layout.addWidget(self.level_combo_box)
        
        self.report_ui = QtWidgets.QTextEdit()
        self.report_ui.setReadOnly(True)
        
        main_layout.addWidget(report_style_widget)
        main_layout.addWidget(self.report_ui)
    
    def update_verbosity_level(self, index):
        self.verbosity_level = index
        self.verbosity_signal.emit()
        
    def render_report(self, result_object, all_check_widgets):
        error_object = result_object['error_object']
        html = ""
        last_failed = False
        self.report_ui.clear()
        for check_widget in all_check_widgets:
            check = check_widget.check
            if check.name in error_object:
                html += check.render_html(error_object[check.name], self.verbosity_level, last_failed)
            last_failed = check.name in error_object
        self.report_ui.insertHtml(html)
    
    def clear(self):
        self.report_ui.clear()
        